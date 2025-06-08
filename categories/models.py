from operator import mod
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
CATEGORY_TYPES = [
    ("income", "Income"),
    ("expense", "Expense"),
    ("savings", "Savings"),
    ("refund", "Refunds"),
]


class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    category_type = models.CharField(
        max_length=100, choices=CATEGORY_TYPES, default="income"
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="subcategories",
    )

    def __str__(self) -> str:
        return f"{self.name}"
