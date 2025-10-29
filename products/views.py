import re
from typing import Any
from django.db.models import QuerySet
from django.views.generic import ListView, DetailView 
from .models import Category, Product, ProductImage 

class ProductListView(ListView):
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products" 
    
    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()
        slug = self.kwargs.get("category_slug")
        if slug:
            queryset = queryset.filter(category__slug=slug)
        return queryset 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        
        return context
        

class ProductDetailView(DetailView):
    model = Product 
    template_name = "products/product_detail.html" 
    context_object_name = "product" 
    slug_url_kwarg = "slug" 
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs) 
        context["related_products"] = Product.objects.filter(
            category=self.object.category).exclude(uid=self.object.uid)[:4]
        return context 


    
    
