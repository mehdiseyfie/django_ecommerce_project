from django.core.cache import cache
import json
import logging
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP

import requests
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import F, Sum
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from cart.models import Cart, CartItem
from customers.models import Profile

from .models import Discount, Order, OrderItem, Payment, ShippingAddress

logger = logging.getLogger(__name__)


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.filter(customer__user=self.request.user).order_by('-created_at')


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'

    def get_queryset(self):
        return Order.objects.filter(customer__user=self.request.user)


@method_decorator(csrf_protect, name='dispatch')
class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    template_name = 'orders/order_create.html'
    fields = ['shipping_address', 'billing_address', 'shipping_method']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            profile = Profile.objects.get(user=self.request.user)
            cart = profile.cart  # type: ignore
            context['cart'] = cart
            context['shipping_addresses'] = ShippingAddress.objects.filter(customer=profile)
        except Profile.DoesNotExist:
            context['error'] = "User profile does not exist."
            context['cart'] = None
        return context

    def form_valid(self, form):
        try:
            with transaction.atomic():
                profile = Profile.objects.get(user=self.request.user)
                cart = profile.cart  # type: ignore

                if not cart.is_active or cart.total_items == 0:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Your cart is empty or inactive. Please add items to your cart.'
                    }, status=400)

                # Check stock availability
                for cart_item in cart.cartitems.all():
                    if cart_item.product.stock < cart_item.quantity:
                        return JsonResponse({
                            'status': 'error',
                            'message': f'Insufficient stock for {cart_item.product.name}'
                        }, status=400)

                # Create order without saving yet
                order = form.save(commit=False)
                order.customer = profile
                order.cart = cart
                order.total_price = Decimal(str(cart.total_price))
                order.total_items = cart.total_items
                order.status = 'pending'
                order.payment_status = 'pending'

                # محاسبه shipping_cost
                shipping_rates = {
                    'standard': Decimal('100000.00'),
                    'express': Decimal('200000.00'),
                    'overnight': Decimal('300000.00'),
                    'pickup': Decimal('0.00'),
                }
                order.shipping_cost = shipping_rates.get(order.shipping_method, Decimal('100000.00'))

                # محاسبه مالیات
                order.tax_amount = (order.total_price * Decimal('0.09')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

                # اعمال تخفیف
                discount_code = self.request.POST.get('discount_code')
                order.discount_amount = Decimal('0.00')
                if discount_code:
                    try:
                        discount = Discount.objects.get(code=discount_code, is_active=True)
                        order.discount_amount = discount.apply_discount(order.total_price)
                        discount.used_count += 1
                        discount.save()
                    except Discount.DoesNotExist:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Invalid or inactive discount code.'
                        }, status=400)

                # ذخیره اولیه بدون clean
                order.save(skip_totals=True)

                # Create order items and reduce stock
                for cart_item in cart.cartitems.all():
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price=Decimal(str(cart_item.price))
                    )
                    cart_item.product.stock -= cart_item.quantity
                    cart_item.product.save()

                # محاسبه totals
                order.calculate_totals()

                # ذخیره نهایی
                order.save()

                # Deactivate cart
                cart.is_active = False
                cart.is_ordered = True
                cart.save()

                # Payment initiation
                zarinpal_request_url = "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
                payment_data = {
                    'merchant_id': '0b3dee3a-0d93-46d3-a681-a46bc9ad1847',
                    'amount': int(order.get_total_amount() * 10),  # Rials
                    'description': f'Payment for Order #{order.uid}',
                    'callback_url': self.request.build_absolute_uri(reverse('orders:payment_callback')),
                }
                if self.request.user.email: #type:ignore
                    payment_data['email'] = self.request.user.email #type:ignore
                if hasattr(self.request.user, 'phone') and self.request.user.phone:#type:ignore
                    payment_data['mobile'] = str(self.request.user.phone)#type:ignore 

                response = requests.post(zarinpal_request_url, json=payment_data, timeout=10)
                if response.status_code != 200:
                    return JsonResponse({'status': 'error', 'message': 'Payment service unavailable'}, status=500)

                result = response.json()
                if result.get('data', {}).get('code') == 100:
                    authority = result['data']['authority']
                    Payment.objects.create(
                        order=order,
                        payment_id=authority,
                        authority=authority,
                        amount=order.get_total_amount(),
                        gateway='zarinpal',
                        status='pending'
                    )
                    return HttpResponseRedirect(f"https://sandbox.zarinpal.com/pg/StartPay/{authority}")
                else:
                    return JsonResponse({'status': 'error', 'message': 'Payment request failed'}, status=500)

        except Exception as e:
            logger.exception("Error in order creation")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@method_decorator(csrf_protect, name='dispatch')
class PaymentCallbackView(View):
    def get(self, request, *args, **kwargs):
        authority = request.GET.get('Authority')
        status = request.GET.get('Status')

        try:
            payment = Payment.objects.get(authority=authority)
            order = payment.order
            cart = Cart.objects.filter(customer__user=self.request.user).first()

            if status == 'OK':
                zarinpal_verify_url = "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"
                verify_data = {
                    'merchant_id': '0b3dee3a-0d93-46d3-a681-a46bc9ad1847',
                    'amount': int(order.get_total_amount() * 10),
                    'authority': authority,
                }
                response = requests.post(zarinpal_verify_url, json=verify_data, timeout=10)
                if response.status_code == 200:
                    result = response.json()
                    if result.get('data', {}).get('code') == 100:
                        payment.ref_id = result['data']['ref_id']
                        payment.status = 'completed'
                        payment.gateway_response = json.dumps(result)
                        payment.save()

                        order.payment_status = 'paid'
                        order.status = 'confirmed'
                        order.save()
                        if cart:
                            CartItem.objects.filter(cart=cart).delete()
                            cart.total_items = 0
                            cart.is_active = False  # غیرفعال کردن سبد خرید
                            cart.is_ordered = True
                            cart.save()
                            cache.delete(f"cart_items_{cart.slug}")
                            cache.delete(f"cart_totals_{cart.slug}")

                        # Send email notification
                        send_mail(
                            f"Payment Successful for Order #{order.uid}",
                            f"Your payment for order #{order.uid} was successful. Ref ID: {payment.ref_id}",
                            'from@example.com',
                            [order.customer.user.email],
                            fail_silently=False,
                        )

                        return render(request, 'orders/payment_success.html', {'order': order, 'payment': payment})
                    else:
                        payment.status = 'failed'
                        payment.save()
                        return render(request, 'orders/payment_failed.html', {'order': order, 'payment': payment, 'error': 'Verification failed'})
                else:
                    payment.status = 'failed'
                    payment.save()
                    return render(request, 'orders/payment_failed.html', {'order': order, 'payment': payment, 'error': 'Verification service unavailable'})
            else:
                payment.status = 'failed'
                payment.save()
                return render(request, 'orders/payment_failed.html', {'order': order, 'payment': payment, 'error': 'Payment cancelled'})

        except Payment.DoesNotExist:
            return render(request, 'orders/payment_failed.html', {'error': 'Payment not found'})
        except Exception as e:
            logger.exception("Error in payment callback")
            return render(request, 'orders/payment_failed.html', {'error': str(e)})


class OrderUpdateView(LoginRequiredMixin, UpdateView):
    model = Order
    template_name = 'orders/order_update.html'
    fields = ['status', 'shipping_method', 'tracking_number']
    pk_url_kwarg = 'order_id'

    def get_queryset(self):
        return Order.objects.filter(customer__user=self.request.user)

    def form_valid(self, form):
        order = form.save(commit=False)
        if form.cleaned_data['status'] == 'paid' and order.payment_status != 'paid':
            return JsonResponse({'status': 'error', 'message': 'Cannot set status to paid without payment'}, status=400)
        return super().form_valid(form)


class OrderDeleteView(LoginRequiredMixin, DeleteView):
    model = Order
    template_name = 'orders/order_delete.html'
    pk_url_kwarg = 'order_id'

    def get_queryset(self):
        return Order.objects.filter(customer__user=self.request.user, status='pending')

    def get_success_url(self):
        return reverse('orders:order_list')


class PaymentVerifyView(LoginRequiredMixin, View):
    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        try:
            payment_id = request.POST.get('payment_id')
            payment = Payment.objects.get(payment_id=payment_id)
            return JsonResponse({'status': 'success', 'order_id': payment.order.uid, 'payment_status': payment.status})
        except Payment.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Payment not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)