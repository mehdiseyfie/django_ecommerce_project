from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from .models import Profile

class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile 
    template_name = "customers/profile_detail.html"
    context_object_name = "profile"  
    
    def get_object(self, queryset: QuerySet | None = None) -> Profile:
        profile = getattr(self.request.user, "profile") 
        return profile 
            