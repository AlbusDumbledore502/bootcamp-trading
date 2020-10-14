from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class UserAcount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    balance = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.user.username

class Stock(models.Model):
    market = models.CharField(max_length=50)
    stock = models.CharField(max_length=50)

    def __str__(self):
        return self.stock

class UserPortfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateField()
    balance = models.FloatField()

    def __str__(self):
        return self.user.username

class TradeHistory(models.Model):
    TRADE_TYPES = (
        ('Buy', 'Buy'),
        ('Sold', 'Sold'),
    )

    PAYMENT_MODES = (
        ('Card', 'Card'),
        ('Wallet', 'Wallet')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    stock = models.CharField(max_length=10, blank=True, null=True)
    type = models.CharField(max_length=4, choices=TRADE_TYPES)
    date = models.DateField()
    payment_mode = models.CharField(max_length=10, choices=PAYMENT_MODES)
    payment_description = models.CharField(max_length=100)
    units = models.FloatField()
    unit_price = models.FloatField()
    total_price = models.FloatField()

    def __str__(self):
        return self.username + self.stock
