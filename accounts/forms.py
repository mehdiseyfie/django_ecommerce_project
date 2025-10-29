# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from allauth.account.forms import SignupForm
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
from .models import CustomUser
from typing import cast 


# =========================
# فرم ثبت‌نام سایت (Allauth)
# =========================
class CustomSignupForm(SignupForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={"autocomplete": "email"})
    )
    phone = PhoneNumberField(
        label=_("Phone number"),
        required=True,
        widget=forms.TextInput(attrs={"autocomplete": "tel"})
    )
    address = forms.CharField(
        label=_("Address"),
        required=False,
        widget=forms.Textarea(
            attrs={
                "row": 3,
                "placeholder": _("Enter your address"),
                "autocomplete": "street-address"
            }
        )
    )
    first_name = forms.CharField(
        label=_("First name"),
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'autocomplete': 'given-name'}),
    )
    last_name = forms.CharField(
        label=_("Last name"),
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'autocomplete': 'family-name'}),
    )

    class Meta:
        model = CustomUser
        fields = ("email", "phone", "first_name", "last_name")
        
        
    def save(self, request):
        user = cast(CustomUser, super().save(request))
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        user.phone = self.cleaned_data.get("phone")
        user.address = self.cleaned_data.get("address", "")
        user.save()
        return user

# =========================
# فرم ادمین برای ایجاد کاربر
# =========================
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'}),
    )
    phone = forms.CharField(
        label=_("Phone number"),
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'autocomplete': 'tel'}),
    )

    class Meta(UserCreationForm.Meta):  # type: ignore
        model = CustomUser
        fields = ("email", "phone", "first_name", "last_name")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and self._meta.model.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("A user with that email already exists"))
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        try:
            parsed_phone = PhoneNumber.from_string(phone)
            if not parsed_phone.is_valid():
                raise forms.ValidationError(_("Invalid phone number"))
            if self._meta.model.objects.filter(phone=parsed_phone).exists():
                raise forms.ValidationError(_("A user with that phone number already exists"))
            return parsed_phone
        except Exception:
            raise forms.ValidationError(_("Invalid phone number format"))


# =========================
# فرم تغییر کاربر (ادمین)
# =========================
class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):  # type: ignore
        model = CustomUser
        fields = (
            "email",
            "phone",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_superuser"
        )
