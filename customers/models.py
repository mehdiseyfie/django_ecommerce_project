from tabnanny import verbose
from django.db import models
from accounts.models import CustomUser 
from django.utils.translation import gettext_lazy as _ 
from django.conf import settings 
from base.models import BaseModel

class Profile(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    
    class Meta:
        verbose_name = _("Customer Profile")
        verbose_name_plural = _("Customer Profile")
        
    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name} - email: {self.user.email}, phone: {self.user.phone}"




