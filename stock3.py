from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.core.cache import cache
from django.core.exceptions import ValidationError
import json
from .models import Cart, CartItem
from products.models import Product

class CartView(LoginRequiredMixin, View):
    """
    نمایش و مدیریت سبد خرید کاربر
    GET: نمایش آیتم‌های سبد
    POST: افزودن آیتم جدید یا دسته‌ای
    """
    template_name = 'cart/cart_list.html'

    def setup(self, request, *args, **kwargs):
        """تنظیم اولیه: دریافت سبد کاربر"""
        super().setup(request, *args, **kwargs)
        self.cart = get_object_or_404(
            Cart, customer__user=request.user, is_active=True)

    def get(self, request, *args, **kwargs):
        """نمایش آیتم‌های سبد خرید با کشینگ"""
        cache_key = f"cart_items_{self.cart.slug}"
        cart_items = cache.get(cache_key)
        if not cart_items:
            cart_items = CartItem.objects.filter(
                cart=self.cart
            ).select_related('product').order_by('-created_at')
            cache.set(cache_key, list(cart_items), timeout=3600)  # 1 ساعت کش
        context = {
            'cart': self.cart,
            'cart_items': cart_items,
            'total_price': self.cart.total_price,
            'total_items': self.cart.total_items,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs): 
        """افزودن آیتم یا دسته‌ای به سبد"""
        try:
            with transaction.atomic():
                action = request.POST.get('action')
                if action == 'add_single':
                    product_id = request.POST.get('product_id')
                    quantity = int(request.POST.get('quantity', 1))
                    product = get_object_or_404(Product, pk=product_id)
                    cart_item = CartItem(
                        cart=self.cart,
                        product=product,
                        quantity=quantity,
                        price=product.price
                    )
                    cart_item.save()
                    cache.delete(f"cart_items_{self.cart.slug}")
                    return JsonResponse({'status': 'success', 'message': 'Item added'})

                else:
                    return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)
        except ValidationError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Server error'}, status=500)

    def http_method_not_allowed(self, request, *args, **kwargs):
        """پاسخ سفارشی برای متدهای غیرمجاز"""
        return JsonResponse({
            'status': 'error',
            'message': f'Method {request.method} not allowed'
        }, status=405)

class CartItemUpdateView(LoginRequiredMixin, View):
    """
    به‌روزرسانی آیتم سبد
    PUT: تغییر تعداد یا قیمت آیتم
    """
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.cart = get_object_or_404(Cart, customer__user=request.user, is_active=True)
        self.cart_item = get_object_or_404(CartItem, pk=kwargs.get('item_id'), cart=self.cart)

    def put(self, request, *args, **kwargs):
        """به‌روزرسانی تعداد یا قیمت آیتم"""
        try:
            with transaction.atomic():
                data = json.loads(request.body)
                old_quantity = self.cart_item.quantity
                old_price = self.cart_item.price
                self.cart_item.quantity = data.get('quantity', self.cart_item.quantity)
                self.cart_item.price = data.get('price', self.cart_item.price)
                self.cart_item.save(old_quantity=old_quantity, old_price=old_price)
                cache.delete(f"cart_items_{self.cart.slug}")
                return JsonResponse({'status': 'success', 'message': 'Item updated'})
        except ValidationError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Server error'}, status=500)

class CartItemDeleteView(LoginRequiredMixin, View):
    """
    حذف آیتم از سبد
    DELETE: حذف یک آیتم خاص
    """
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.cart = get_object_or_404(Cart, customer__user=request.user, is_active=True)
        self.cart_item = get_object_or_404(CartItem, pk=kwargs.get('item_id'), cart=self.cart)

    def delete(self, request, *args, **kwargs):
        """حذف آیتم از سبد"""
        try:
            with transaction.atomic():
                self.cart_item.delete() 
                cache.delete(f"cart_items_{self.cart.slug}")
                return JsonResponse({'status': 'success', 'message': 'Item deleted'})
        except ValidationError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Server error'}, status=500)
        
class CartClearView(LoginRequiredMixin, View):
    """
    پاک کردن کامل سبد خرید
    POST: حذف تمام آیتم‌ها و غیرفعال کردن سبد
    """
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.cart = get_object_or_404(Cart, customer__user=request.user, is_active=True)

    def post(self, request, *args, **kwargs):
        """پاک کردن سبد"""
        try:
            with transaction.atomic():
                CartItem.objects.filter(cart=self.cart).delete()
                self.cart.is_active = False
                self.cart.total_items = 0
                self.cart.total_price = 0
                self.cart.save(update_fields=['is_active', 'total_items', 'total_price'])
                cache.delete(f"cart_items_{self.cart.slug}")
                cache.delete(f"cart_totals_{self.cart.slug}")
                return JsonResponse({'status': 'success', 'message': 'Cart cleared'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Server error'}, status=500)