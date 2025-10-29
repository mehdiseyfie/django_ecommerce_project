from django.urls import path , include 
from .views import ProductListView, ProductDetailView

app_name = "products"

urlpatterns = [
    path("", ProductListView.as_view(), name="product_list"),
    path("category/<slug:category_slug>/", ProductListView.as_view(), name="category"),
    path("<slug:slug>/", ProductDetailView.as_view(), name="profile_detail"),
 
]
