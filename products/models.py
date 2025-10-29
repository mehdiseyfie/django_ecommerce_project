from django.conf import settings
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from base.models import BaseModel


class Category(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(
        upload_to='category_images/', blank=True, null=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self) -> str:
        return self.name
    
class Product(BaseModel):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE,
        to_field="uid",related_name="products")
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    available = models.BooleanField(default=True)
    newes_product = models.BooleanField(default=False) 
    
    class Meta:
        ordering = ["-name"]
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    def __str__(self) -> str:
        return self.name 
    
class ProductImage(BaseModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, 
        to_field="uid",
        related_name="product_images")
    image = models.ImageField(
        upload_to="products_images", null=True, blank=True)
    
    def img_preview(self):
        return mark_safe(
            f'<img src="{self.image.url}" width="100" height="100" />') #type:ignore
    img_preview.short_description = "Image Preview"
    img_preview.allow_tags = True
    
    class Meta:
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")
        
    def __str__(self) -> str:
        return self.product.name
    def save(self, *args, **kwargs):
        if not self.image:
            self.image = "default_product_image.jpg"
        super().save(*args, **kwargs)
    
class Review(BaseModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        to_field="uid",
        related_name="reviews")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField()
    comment = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")
        
    def __str__(self) -> str:
        return f"{self.rating} by {self.user.username} for {self.product.name}"
    
    
    def save(self, *args, **kwargs):
        if self.rating < 1 or self.rating > 5:
            raise ValueError("Rating must be between 1 and 5")
        super().save(*args, **kwargs)





























