from django.contrib import admin
from .models import Order, OrderItem, Payment, ShippingAddress

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['uid', 'customer', 'total_price', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['customer__user__email', 'uid']
    readonly_fields = ['total_price', 'total_items']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('customer__user', 'cart')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'get_total_price_item']
    list_filter = ['order__status']
    search_fields = ['product__name', 'order__uid']

    def get_total_price_item(self, obj):
        return f"${obj.get_total_price_item():.2f}"
    get_total_price_item.short_description = 'Total Price'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'uid', 'amount', 'gateway', 'status', 'created_at']
    list_filter = ['gateway', 'status']
    search_fields = ['payment_uid', 'order__uid']

@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['customer', 'first_name', 'last_name', 'city', 'country', 'is_default']
    list_filter = ['is_default', 'country']
    search_fields = ['first_name', 'last_name', 'city']