from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from .models import Stock

class UserRegistrationFrom(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']


class StockRegistrationForm(forms.ModelForm):
    MARKET_CHOICES = (
        ('NASDAQ', 'NASDAQ'),
    )
    market = forms.ChoiceField(choices = MARKET_CHOICES)

    class Meta:
        model = Stock
        fields = ['market', 'stock']
