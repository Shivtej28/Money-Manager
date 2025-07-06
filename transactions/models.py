from django.db import models
from django.contrib.auth.models import User
from categories.models import Category
from banks.models import Banks


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
        return self.subcategory and self.subcategory.category_type == "savings"

    def get_saving_bank(self):
        return Banks.objects.filter(user=self.user, account_type="savings").first()

    def save(self, *args, **kwargs):
        """Update bank balance when a transaction is added or updated."""
        if self.pk:  # If updating an existing transaction
            old_transaction = Transaction.objects.get(pk=self.pk)
            old_subcat = old_transaction.subcategory

            if old_subcat:
                if old_subcat.category_type == "expense":
                    old_transaction.bank.balance += old_transaction.amount
                elif old_subcat.category_type == "income":
                    old_transaction.bank.balance -= old_transaction.amount
                elif old_subcat.category_type == "refund":
                    old_transaction.bank.balance -= old_transaction.amount
                elif old_subcat.category_type == "savings":
                    old_saving_bank = old_transaction.get_saving_bank()
                    if old_saving_bank:
                        old_saving_bank.balance -= old_transaction.amount
                        old_transaction.bank.balance += old_transaction.amount
                        old_saving_bank.save()

            old_transaction.bank.save()

        if self.subcategory:
            if self.subcategory.category_type == "savings":
                saving_bank = self.get_saving_bank()
                if saving_bank:
                    saving_bank.balance += self.amount
                    self.bank.balance -= self.amount
                    saving_bank.save()

            if self.subcategory.category_type == "expense":
                self.bank.balance -= self.amount
            elif self.subcategory.category_type == "income":
                self.bank.balance += self.amount
            elif self.subcategory.category_type == "refund":
                self.bank.balance += self.amount

            if self.subcategory.parent:
                self.category = self.subcategory.parent

        self.bank.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Revert balances when deleting a transaction"""
        subcat = self.subcategory

        if subcat:
            if subcat.category_type == "expense":
                self.bank.balance += self.amount
            elif subcat.category_type == "income":
                self.bank.balance -= self.amount
            elif subcat.category_type == "refund":
                self.bank.balance -= self.amount
            elif subcat.category_type == "savings":
                saving_bank = self.get_saving_bank()
                if saving_bank:
                    saving_bank.balance -= self.amount
                    self.bank.balance += self.amount
                    saving_bank.save()

            self.bank.save()

        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.category} - ₹{self.amount} ({self.transaction_date})"
