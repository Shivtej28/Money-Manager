from ast import mod
from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Banks(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    account_type = models.CharField(max_length=100, default="savings")

    def __str__(self) -> str:
        return f"Bank: {self.name} Balance: {self.balance}"
