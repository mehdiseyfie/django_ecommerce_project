from decimal import ROUND_HALF_UP, ROUND_DOWN, Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Sum
from django.utils.translation import gettext_lazy as _

from base.models import BaseModel
from cart.models import Cart
from customers.models import Profile
from products.models import Product


class Order(BaseModel):
    ORDER_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('processing', _('Processing')),
        ('shipped', _('Shipped')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled')),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('paid', _('Paid')),
        ('failed', _('Failed')),
        ('refunded', _('Refunded')),
    ]
    SHIPPING_METHOD_CHOICES = [
        ('standard', _('Standard Shipping')),
        ('express', _('Express Shipping')),
        ('overnight', _('Overnight Shipping')),
        ('pickup', _('Store Pickup')),
    ]

    customer = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="orders", verbose_name=_("Customer")
    )
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="orders",
        to_field="uid",
        verbose_name=_("Cart")
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name=_("Total Price")
    )
    total_items = models.PositiveIntegerField(
        verbose_name=_("Total Items"), null=True, blank=True, default=None
    )
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='pending', verbose_name=_("Status")
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending', verbose_name=_("Payment Status")
    )
    payment_gateway = models.CharField(max_length=50, default='zarinpal', verbose_name=_("Payment Gateway"))
    tracking_number = models.CharField(max_length=100, blank=True, verbose_name=_("Tracking Number"))
    shipping_address = models.ForeignKey(
        'ShippingAddress', on_delete=models.SET_NULL, null=True,
        related_name='orders_shipping', verbose_name=_("Shipping Address")
    )
    billing_address = models.ForeignKey(
        'ShippingAddress', on_delete=models.SET_NULL, null=True,
        related_name='orders_billing', verbose_name=_("Billing Address")
    )
    shipping_method = models.CharField(
        max_length=20,
        choices=SHIPPING_METHOD_CHOICES,
        default='standard', verbose_name=_("Shipping Method")
    )
    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    tax_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.00, verbose_name=_("Discount Amount")
    )

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        ordering = ['-created_at']


    def calculate_tax(self):
        """محاسبه مالیات بر اساس orderitems یا total_price"""
        if self.pk and self.orderitems.exists(): #type: ignore
            subtotal = sum(item.get_total_price_item() for item in self.orderitems.all()) #type: ignore
        else:
            subtotal = Decimal(str(self.total_price))  # تبدیل صریح به Decimal
        tax_rate = Decimal('0.09')
        return (subtotal * tax_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def clean(self):
        """اعتبارسنجی مقادیر و تطابق قیمت‌ها"""
        super().clean()
        # تبدیل صریح تمام مقادیر به Decimal
        self.total_price = Decimal(str(self.total_price))
        self.tax_amount = Decimal(str(self.tax_amount))
        self.discount_amount = Decimal(str(self.discount_amount))
        self.shipping_cost = Decimal(str(self.shipping_cost))

        if self.total_price < 0:
            raise ValidationError("Total price cannot be negative.")
        if self.total_items is not None and self.total_items < 0:  # اجازه دادن به total_items=0
            raise ValidationError("Total items cannot be negative.")
        if self.payment_status == 'paid' and self.status == 'pending':
            raise ValidationError("Paid orders cannot be pending.")
        if self.discount_amount > self.total_price:
            raise ValidationError("Discount cannot exceed total price.")
        if self.tax_amount < 0:
            raise ValidationError("Tax amount cannot be negative.")

        # اعتبارسنجی تطابق total_price فقط برای نمونه‌های ذخیره‌شده
        if self.pk and self.customer_id: # type: ignore
            expected_total = sum(item.get_total_price_item() for item in self.orderitems.all()) # type: ignore
            if abs(self.total_price - expected_total) > Decimal('0.01'):
                raise ValidationError("Total price does not match sum of order items.")

        # تنظیم tax_amount فقط اگر صفر باشد و total_price مثبت باشد
        if self.tax_amount == Decimal('0.00') and self.total_price > 0:
            self.tax_amount = self.calculate_tax()

    def save(self, *args, skip_totals=False, **kwargs):
        """سفارشی‌سازی ذخیره برای اطمینان از مقادیر معتبر"""
        self.total_price = Decimal(str(self.total_price)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        self.tax_amount = Decimal(str(self.tax_amount)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        self.discount_amount = Decimal(str(self.discount_amount)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        self.shipping_cost = Decimal(str(self.shipping_cost)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        
        if not self.customer_id: #type: ignore
            raise ValidationError("Customer is required for Order.")
        
        # فقط اگر skip_totals=False باشد، full_clean اجرا شود
        if not skip_totals:
            self.full_clean()
        
        super().save(*args, **kwargs)
        
        if not skip_totals and self.pk and self.orderitems.exists(): #type: ignore
            self.calculate_totals()

    def calculate_totals(self):
        """محاسبه مجموع قیمت و تعداد آیتم‌ها با تجمیع دیتابیس"""
        totals = self.orderitems.aggregate( # type: ignore
            total_price=Sum(F('quantity') * F('price')),
            total_items=Sum('quantity')
        )
        self.total_price = Decimal(str(totals['total_price'] or 0)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        self.total_items = totals['total_items'] or 0
        self.save(skip_totals=True, update_fields=['total_price', 'total_items'])

    def get_total_amount(self):
        return self.total_price + self.shipping_cost + self.tax_amount - self.discount_amount

    def __str__(self):
        return f"Order {self.uid} - {self.customer.user.email} - {self.status}"

class OrderItem(BaseModel):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="orderitems",
        to_field="uid",
        verbose_name=_("Order")
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name=_("Product")
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name=_("Quantity"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")
        ordering = ['product__name']

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("Quantity must be positive.")
        if self.price < 0:
            raise ValidationError("Price cannot be negative.")

    def get_total_price_item(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.uid}"

class Discount(BaseModel):
    code = models.CharField(max_length=50, unique=True, verbose_name=_("Discount Code"))
    discount_type = models.CharField(
        max_length=20,
        choices=[('percentage', _('Percentage')), ('fixed', _('Fixed Amount'))],
        default='percentage',
        verbose_name=_("Discount Type")
    )
    value = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_("Discount Value")
    )
    valid_from = models.DateTimeField(verbose_name=_("Valid From"))
    valid_until = models.DateTimeField(verbose_name=_("Valid Until"))
    max_usage = models.PositiveIntegerField(default=0, verbose_name=_("Max Usage"))
    used_count = models.PositiveIntegerField(default=0, verbose_name=_("Used Count"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    class Meta:
        verbose_name = _("Discount")
        verbose_name_plural = _("Discounts")

    def clean(self):
        if self.value < 0:
            raise ValidationError("Discount value cannot be negative.")
        if self.max_usage < 0:
            raise ValidationError("Max usage cannot be negative.")
        if self.used_count < 0:
            raise ValidationError("Used count cannot be negative.")
        if self.valid_from > self.valid_until:
            raise ValidationError("Valid from date must be before valid until date.")

    def apply_discount(self, total_price):
        """محاسبه تخفیف بر اساس نوع و مقدار"""
        if not self.is_active or self.used_count >= self.max_usage > 0:
            return Decimal('0.00')
        if self.discount_type == 'percentage':
            return (total_price * (self.value / 100)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        return self.value.quantize(Decimal('0.01'), rounding=ROUND_DOWN)

    def __str__(self):
        return f"{self.code} - {self.get_discount_type_display()} {self.value}" # type: ignore
    
    
class Payment(BaseModel):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment", verbose_name=_("Order"))
    payment_id = models.CharField(max_length=100, unique=True, verbose_name=_("Payment ID"))
    authority = models.CharField(max_length=100, blank=True, verbose_name=_("Authority"))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Amount"))
    gateway = models.CharField(max_length=50, default='zarinpal', verbose_name=_("Payment Gateway"))
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed'), ('refunded', 'Refunded')],
        default='pending', verbose_name=_("Status")
    )
    ref_id = models.CharField(max_length=100, blank=True, verbose_name=_("Ref ID"))
    transaction_id = models.CharField(max_length=100, blank=True, verbose_name=_("Transaction ID"))
    gateway_response = models.TextField(blank=True, verbose_name=_("Gateway Response"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")
        ordering = ['-created_at']

    def clean(self):
        if self.amount < 0:
            raise ValidationError("Payment amount cannot be negative.")
        if self.status == 'completed' and self.order.payment_status != 'paid':
            raise ValidationError("Completed payment requires order payment status to be paid.")

    def __str__(self):
        return f"Payment {self.payment_id} for Order {self.order.uid}"

class ShippingAddress(BaseModel):
    customer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="shipping_addresses", verbose_name=_("Customer"))
    first_name = models.CharField(max_length=100, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=100, verbose_name=_("Last Name"))
    company = models.CharField(max_length=200, blank=True, verbose_name=_("Company"))
    address_line_1 = models.CharField(max_length=200, verbose_name=_("Address Line 1"))
    address_line_2 = models.CharField(max_length=200, blank=True, verbose_name=_("Address Line 2"))
    city = models.CharField(max_length=100, verbose_name=_("City"))
    state = models.CharField(max_length=100, verbose_name=_("State"))
    postal_code = models.CharField(max_length=20, verbose_name=_("Postal Code"))
    country = models.CharField(max_length=100, verbose_name=_("Country"))
    phone = models.CharField(max_length=20, verbose_name=_("Phone"))
    is_default = models.BooleanField(default=False, verbose_name=_("Default Address"))

    class Meta:
        verbose_name = _("Shipping Address")
        verbose_name_plural = _("Shipping Addresses")

    def save(self, *args, **kwargs):
        if self.is_default:
            ShippingAddress.objects.filter(customer=self.customer, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.city}, {self.country}"