from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from base.models import BaseModel
from customers.models import Profile
from products.models import Product
from django.core.cache import cache
from django.db.models import Sum, F


class Cart(BaseModel):
    """
    سبد خرید مشتری
    شامل مجموع قیمت، تعداد آیتم‌ها و وضعیت فعال/سفارش شده
    """
    customer = models.OneToOneField(
        Profile, on_delete=models.CASCADE,
        related_name="cart",
        to_field="uid",
        verbose_name=_("Customer")
    )

    total_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0.00, verbose_name=_("Total Price")
    )
    total_items = models.PositiveIntegerField(
        default=0, verbose_name=_("Total Items")
    )

    is_active = models.BooleanField(default=True)
    is_ordered = models.BooleanField(default=False)
    slug = models.SlugField(max_length=225, unique=True, blank=True)

    class Meta:
        verbose_name = _("Cart")
        verbose_name_plural = _("Carts")

    def save(self, *args, **kwargs):
        """تولید خودکار اسلاگ براساس ایمیل مشتری"""
        if not self.slug:
            self.slug = slugify(f"cart-{self.customer.user.email}")
        self.clean()
        super().save(*args, **kwargs)
        cache.delete(f"cart_totals_{self.slug}") 
    
    def clean(self):
        """اعتبارسنجی مقادیر منفی"""
        if self.total_price < 0 or self.total_items < 0:
            raise ValidationError("Total price or items cannot be negative.")
    def calculate_totals(self):
        """محاسبه مجموع قیمت و تعداد آیتم‌ها با تجمیع دیتابیس"""
        totals = self.cartitems.aggregate( # type: ignore
            total_price=Sum(F('quantity') * F('price')),
            total_items=Sum('quantity')
        )
        self.total_price = totals['total_price'] or 0
        self.total_items = totals['total_items'] or 0
        self.save()
        
    def __str__(self):
        return f"Cart of {self.customer.user.email}"


class CartItem(BaseModel):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE,
        related_name="cartitems",
        to_field="uid",
        verbose_name=_("Cart")
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name="cart_products", 
        to_field="uid",
        verbose_name=_("Product")
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = _("Cart Item")
        verbose_name_plural = _("Cart Items")
        ordering = ["-created_at"]

    def clean(self):
        """اعتبارسنجی مقدار و قیمت"""
        if self.quantity <= 0:
            raise ValidationError("Quantity must be positive.")
        if self.price < 0:
            raise ValidationError("Price cannot be negative.")
        if self.product and self.quantity > self.product.stock:
            raise ValidationError(f"Insufficient stock for {self.product.name}")
        
    def get_total_price_item(self):
        return self.price * self.quantity

    def save(self, *args, old_quantity=None, old_price=None, **kwargs):
        """ذخیره و به‌روزرسانی افزایشی مجموع سبد خرید"""
        try:
            with transaction.atomic():
                self.clean()
                if not self.price:
                    if not self.product or self.product.price is None:
                        raise ValidationError("Product price is not set")
                    self.price = self.product.price

                is_new = self._state.adding
                if not is_new and old_quantity is not None and old_price is not None:
                    diff_quantity = self.quantity - old_quantity
                    diff_price = (self.quantity * self.price) - (old_quantity * old_price)
                else:
                    diff_quantity = self.quantity
                    diff_price = self.price * self.quantity

                super().save(*args, **kwargs)

                cart = self.cart
                cart.total_items += diff_quantity
                cart.total_price += diff_price
                cart.clean()
                cart.save(update_fields=["total_items", "total_price"])
        except Exception as e:
            raise ValidationError(f"Error saving CartItem: {str(e)}")


    def delete(self, *args, **kwargs):
        """حذف آیتم و کسر از مجموع سبد خرید"""
        try:
            with transaction.atomic():
                cart = self.cart
                cart.total_items -= self.quantity
                cart.total_price -= (self.price * self.quantity)
                cart.clean()
                super().delete(*args, **kwargs)
                cart.save(update_fields=["total_items", "total_price"])
        except Exception as e:
            raise ValidationError(f"Error deleting CartItem: {str(e)}")

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Cart {self.cart.uid}"
