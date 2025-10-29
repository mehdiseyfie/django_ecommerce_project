from django.urls import path

from .views import (CartItemDeleteView, CartItemUpdateView, CartView,
                    ClearCartView)

app_name = 'cart'

urlpatterns = [
    path('', CartView.as_view(), name='cart_list'),
    path('item/<uuid:item_id>/update/', CartItemUpdateView.as_view(), name='cart_item_update'),
    path('item/<uuid:item_id>/delete/', CartItemDeleteView.as_view(), name='cart_item_delete'),
    path('clear/', ClearCartView.as_view(), name='cart_clear'),
]