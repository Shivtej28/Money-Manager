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

    def is_bank_transfer(self):
        print("Jreufukejwj", self.subcategory.name)
        return self.subcategory.category_type == "savings"

    def get_saving_bank(self):
        return Banks.objects.filter(user=self.user, account_type="savings").first()

    def save(self, *args, **kwargs):
        """Update bank balance when a transaction is added or updated."""
        print("Helloooooooooooooooooooooooo")
        if self.pk:  # If updating an existing transaction
            old_transaction = Transaction.objects.get(pk=self.pk)

            # Reverse the effect of old transaction
            if old_transaction.subcategory.category_type == "expense":
                old_transaction.bank.balance += (
                    old_transaction.amount
                )  # Refund old expense
            elif old_transaction.subcategory.category_type == "income":
                old_transaction.bank.balance -= old_transaction.amount
            elif old_transaction.subcategory.category_type == "refund":
                old_transaction.bank.balance -= old_transaction.amount

            old_transaction.bank.save()

        is_bankTransfer = self.is_bank_transfer()
        print(is_bankTransfer)
        if is_bankTransfer:
            print(self.amount, "----------------------")
            saving_bank = self.get_saving_bank()
            print("Saving Bank", saving_bank)
            saving_bank.balance += self.amount
            self.bank.balance -= self.amount
            saving_bank.save()

        # Apply new transaction
        if self.subcategory.category_type == "expense":
            self.bank.balance -= self.amount
        elif self.subcategory.category_type == "income":
            self.bank.balance += self.amount
        elif self.subcategory.category_type == "refund":
            self.bank.balance += self.amount  # refund adds money back

        self.category = self.subcategory.parent

        self.bank.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Revert balance when deleting a transaction"""
        if self.subcategory.category_type == "expense":
            self.bank.balance += self.amount  # Refund money for expense
        elif self.subcategory.category_type == "income":
            self.bank.balance -= self.amount  # Deduct for income
        elif self.subcategory.category_type == "refund":
            self.bank.balance -= (
                self.amount
            )  # Deduct refund since it was previously added

        self.bank.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.category} - ₹{self.amount} ({self.transaction_date})"
