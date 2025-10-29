from phonenumber_field.modelfields import PhoneNumberField
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin 
from django.utils.translation import gettext_lazy as _
from django.utils import timezone 
from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"), unique=True)
    phone = PhoneNumberField(_("phone number"),unique=True)
    address = models.TextField(_("Address"),blank=True, null=True) 
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_(
            "Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = CustomUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = ("email")
    REQUIRED_FIELDS = ["phone"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        
    def __str__(self) -> str:
        return self.email 

    
