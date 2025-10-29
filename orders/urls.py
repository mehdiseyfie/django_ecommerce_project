from django.urls import path

from .views import (OrderCreateView, OrderDeleteView, OrderDetailView,
                    OrderListView, OrderUpdateView, PaymentCallbackView,
                    PaymentVerifyView)

app_name = 'orders'

urlpatterns = [
    # List and create orders
    path('', OrderListView.as_view(), name='order_list'),
    path('create/', OrderCreateView.as_view(), name='order_create'),
    
    # Order details and management
    path('<uuid:order_id>/', OrderDetailView.as_view(), name='order_detail'),
    path('<uuid:order_id>/update/', OrderUpdateView.as_view(), name='order_update'),
    path('<uuid:order_id>/delete/', OrderDeleteView.as_view(), name='order_delete'),
    
    # Payment handling
    path('payment/callback/', PaymentCallbackView.as_view(), name='payment_callback'),
    path('payment/verify/', PaymentVerifyView.as_view(), name='payment_verify'),
    
    # Additional features
    path('<uuid:order_id>/track/', OrderDetailView.as_view(), name='track_order'),
    path('<uuid:order_id>/invoice/', OrderDetailView.as_view(), name='order_invoice'),
    path('<uuid:order_id>/reorder/', OrderDetailView.as_view(), name='reorder'),
]