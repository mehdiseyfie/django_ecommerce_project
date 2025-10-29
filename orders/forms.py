from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Order, ShippingAddress


class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = [
            'first_name', 'last_name', 'company', 'address_line_1',
            'address_line_2', 'city', 'state', 'postal_code', 'country', 'phone'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line_1': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'required': True}),
            'address_line_2': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'country': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
        }
        labels = {
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'company': _('Company (Optional)'),
            'address_line_1': _('Address Line 1'),
            'address_line_2': _('Address Line 2 (Optional)'),
            'city': _('City'),
            'state': _('State/Province'),
            'postal_code': _('Postal Code'),
            'country': _('Country'),
            'phone': _('Phone Number'),
        }

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['shipping_method', 'first_name', 'last_name', 'email', 
                 'address', 'postal_code', 'city']
        widgets = {
            'shipping_method': forms.Select(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'required': True}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
        }
        labels = {
            'shipping_method': _('Shipping Method'),
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'email': _('Email'),
            'address': _('Address'),
            'postal_code': _('Postal Code'),
            'city': _('City'),
        }