from tabnanny import verbose
from django.contrib import admin
from .models import Cart, CartItem
from django.utils.translation import gettext_lazy as _

# ------------------------------
# CartItem Inline (برای نمایش در CartAdmin)
# ------------------------------
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1   # برای اینکه بتونی آیتم جدید اضافه کنی
    fields = ("product", "quantity", "get_total_price_item")
    readonly_fields = ("get_total_price_item",)

    def get_total_price_item(self, obj):
        return obj.get_total_price_item()
    get_total_price_item.short_description = "Total Price"


# ------------------------------
# Cart Admin
# ------------------------------
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("uid", "customer__user", "total_items", "total_price", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("user__username", "uid")
    inlines = [CartItemInline]
    ordering = ("-created_at",)


# ------------------------------
# CartItem Admin (اختیاری)
# ------------------------------
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity", "get_total_price_item")
    list_filter = ("cart", "product")
    search_fields = ("cart__user__email", "product__name")

    def get_total_price_item(self, obj):
        return obj.get_total_price_item()
    get_total_price_item.short_description = "Total Price"
