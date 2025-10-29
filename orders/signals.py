from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import OrderItem,  Order
from cart.models import CartItem, Cart

@receiver([post_save, post_delete], sender=CartItem)
def update_cart_totals(sender, instance, **kwargs):
    """به‌روزرسانی مجموع سبد خرید هنگام تغییر یا حذف CartItem"""
    cart = instance.cart
    cart.calculate_totals()

@receiver([post_save, post_delete], sender=OrderItem)
def update_order_totals(sender, instance, **kwargs):
    order = instance.order
    if order.orderitems.exists() or kwargs.get('signal') == post_delete:
        order.calculate_totals()