import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views import View

from customers.models import Profile
from products.models import Product

from .models import Cart, CartItem


class CartView(LoginRequiredMixin, View):
    """
    نمایش و مدیریت سبد خرید کاربر
    GET: نمایش آیتم‌های سبد
    POST: افزودن آیتم جدید
    """
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        try:
            profile = Profile.objects.get(user=request.user)

            # Try to reuse any existing Cart for this profile (regardless of is_active).
            # If none exists, create one. If exists but inactive, reactivate it.
            self.cart = Cart.objects.filter(customer=profile).first()
            if self.cart is None:
                self.cart = Cart.objects.create(
                    customer=profile,
                    total_price=0.00,
                    total_items=0,
                    is_active=True
                )
            elif not self.cart.is_active:
                # Reactivate existing cart instead of creating a second (OneToOne prevents second)
                self.cart.is_active = True
                self.cart.save(update_fields=['is_active'])
        except Profile.DoesNotExist:
            raise ValidationError("User profile does not exist.")

    def get(self, request, *args, **kwargs):
        """نمایش آیتم‌های سبد خرید با کشینگ"""
        cache_key = f"cart_items_{self.cart.slug}" #type: ignore
        cart_items = cache.get(cache_key)
        if not cart_items:
            cart_items = CartItem.objects.filter(
                cart=self.cart
            ).select_related('product').order_by('-created_at')
            cache.set(cache_key, list(cart_items), timeout=3600)  # 1 ساعت کش
        context = {
            'cart': self.cart,
            'cart_items': cart_items,
            'total_items': self.cart.total_items, #type: ignore
            'total_price': self.cart.total_price, #type: ignore
        }
        return render(request, "cart/cart.html", context)

    def post(self, request, *args, **kwargs):
        """افزودن آیتم جدید به سبد"""
        try:
            with transaction.atomic():
                product_id = request.POST.get('product_id')
                quantity = int(request.POST.get('quantity', 1))
                product = get_object_or_404(Product, pk=product_id)
    
                item, created = CartItem.objects.get_or_create(
                    cart=self.cart,
                    product=product,
                    defaults={"quantity": quantity, "price": product.price}
                )
                if not created:
                    item.quantity += quantity
                    item.save()
                    
                cache.delete(f"cart_items_{self.cart.slug}") #type: ignore
                cache.delete(f"cart_totals_{self.cart.slug}") #type: ignore
                return JsonResponse({
                    'status': 'success',
                    'message': 'Item added',
                    'total_items': self.cart.total_items, #type: ignore
                    'total_price': float(self.cart.total_price) #type: ignore
                })
        except ValidationError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Server error'}, status=500)

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
                if 'quantity' in data:
                    quantity = data['quantity']
                    if not isinstance(quantity, int) or quantity <= 0:
                        raise ValidationError('Quantity must be a positive integer')
                    self.cart_item.quantity = quantity
                if 'price' in data:
                    price = data['price']
                    if not isinstance(price, (int, float)) or price < 0:
                        raise ValidationError('Price must be non-negative')
                    self.cart_item.price = price
                self.cart_item.save(old_quantity=old_quantity, old_price=old_price)
                cache.delete(f"cart_items_{self.cart.slug}")
                cache.delete(f"cart_totals_{self.cart.slug}")
                return JsonResponse({
                    'status': 'success',
                    'message': 'Item updated',
                    'total_price_item': float(self.cart_item.get_total_price_item()),
                    'total_items': self.cart.total_items,
                    'total_price': float(self.cart.total_price)
                })
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
                cache.delete(f"cart_totals_{self.cart.slug}")
                return JsonResponse({
                    'status': 'success',
                    'message': 'Item deleted',
                    'total_items': self.cart.total_items,
                    'total_price': float(self.cart.total_price)
                })
        except ValidationError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Server error'}, status=500)

class ClearCartView(LoginRequiredMixin, View):
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
                return JsonResponse({
                    'status': 'success',
                    'message': 'Cart cleared',
                    'total_items': 0,
                    'total_price': 0.0
                })
        except ValidationError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Server error'}, status=500)