from django.contrib import admin
from .models import Category, Product, ProductImage 
from django.contrib import admin 
from django.utils.translation import gettext_lazy as _ 

class CategoryAdmin(admin.ModelAdmin):
    model = Category
    list_display = ("name", "slug", "description", "image",)
    search_fields = ("name", "slug",)
    list_filter = ("name", "slug",)
    
    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
admin.site.register(Category, CategoryAdmin) #type: ignore 

class ProductImageInline(admin.TabularInline):
    model = ProductImage 
    extra = 1 

    
class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ("name", "price", "stock", "available", "newes_product",)
    search_fields = ("name", "slug",) 
    ordering = ('name',)
    list_filter = ("category", "newes_product",) 
    
    inlines = [ProductImageInline]
    
admin.site.register(Product, ProductAdmin)

