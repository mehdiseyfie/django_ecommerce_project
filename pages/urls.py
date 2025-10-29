from django.urls import path , include
from .views import HomePageView

app_name = "pages"
urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
]   