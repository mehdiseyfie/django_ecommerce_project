# customers/urls.py
from django.urls import path
from .views import ProfileDetailView 

app_name = "customers"
urlpatterns = [
    path("profile/", ProfileDetailView.as_view(), name="profile_detail"),
]