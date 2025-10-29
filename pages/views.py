from django.shortcuts import render
from django.views.generic import TemplateView
from products.models import Product, Category
# Create your views here.
class HomePageView(TemplateView):
    template_name = "home.html"