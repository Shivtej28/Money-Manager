from operator import mod
from unicodedata import category
from django.db import models
from django.contrib.auth.models import User

from categories.models import Category
from banks.models import Banks

# Create your models here.


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    transaction_date = models.DateField()
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="transactions"
    )
    subcategory = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sub_transactions",
    )
    bank = models.ForeignKey(
        Banks, on_delete=models.CASCADE, related_name="transactions"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        """Update bank balance when a transaction is added or updated."""
        if self.pk:  # If updating an existing transaction
            old_transaction = Transaction.objects.get(pk=self.pk)

            # Reverse the effect of old transaction
            if old_transaction.subcategory.category_type == "expense":
                old_transaction.bank.balance += (
                    old_transaction.amount
                )  # Refund old expense
            else:
                old_transaction.bank.balance -= (
                    old_transaction.amount
                )  # Deduct old income

            old_transaction.bank.save()

        # Apply new transaction
        if self.subcategory.category_type == "expense":
            self.bank.balance -= self.amount
        else:
            self.bank.balance += self.amount

        self.category = self.subcategory.parent

        self.bank.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Revert balance when deleting a transaction"""
        if self.subcategory.category_type == "expense":
            self.bank.balance += self.amount  # Refund money for expense
        else:
            self.bank.balance -= self.amount  # Deduct for income

        self.bank.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.category} - ₹{self.amount} ({self.transaction_date})"
