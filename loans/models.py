from django.db import models
from django.contrib.auth.models import User
from datetime import date
import math


class Loan(models.Model):
    """Stores loan details and links with a category for transaction tracking."""

    STATUS_CHOICES = (("ongoing", "Ongoing"), ("completed", "Completed"))

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    loan_name = models.CharField(max_length=255)
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tenure_months = models.IntegerField(help_text="Total tenure in months")
    start_date = models.DateField(default=date.today)
    category = models.ForeignKey("categories.Category", on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="ongoing")
    interest_rate = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Annual interest rate in %"
    )

    def calculate_emi(self):
        """Calculate EMI using the latest interest rate."""
        latest_rate = self.interest_history.order_by("-start_date").first()
        interest_rate = latest_rate.interest_rate if latest_rate else 0

        P = self.loan_amount
        r = interest_rate / (12 * 100)
        n = self.tenure_months

        if r == 0:
            return P / n

        emi = (P * r * (1 + r) ** n) / ((1 + r) ** n - 1)
        return round(emi, 2)

    def total_paid(self):
        """Total amount paid (EMIs + prepayments) based on category transactions."""
        from transactions.models import Transaction

        return sum(
            Transaction.objects.filter(subcategory=self.category).values_list(
                "amount", flat=True
            )
        )

    def remaining_principal(self):
        """Remaining loan balance after EMI & prepayments."""
        return max(0, self.loan_amount - self.total_paid())

    def total_interest_paid(self):
        """Calculate total interest paid till date considering interest rate changes."""
        from transactions.models import Transaction

        interest_paid = 0
        remaining_principal = self.loan_amount

        transactions = Transaction.objects.filter(subcategory=self.category).order_by(
            "transaction_date"
        )

        for txn in transactions:
            applicable_rate = (
                self.interest_history.filter(start_date__lte=txn.transaction_date)
                .order_by("-start_date")
                .first()
            )

            if applicable_rate:
                monthly_interest_rate = applicable_rate.interest_rate / (12 * 100)
                interest_component = remaining_principal * monthly_interest_rate
                principal_component = txn.amount - interest_component

                interest_paid += interest_component
                remaining_principal -= principal_component

        return round(interest_paid, 2)

    def remaining_interest(self):
        """Calculate remaining interest to be paid."""
        return max(0, self.total_interest() - self.total_interest_paid())

    def remaining_tenure(self):
        """Recalculate remaining tenure based on prepayments & EMIs."""
        principal = self.remaining_principal()
        latest_rate = self.interest_history.order_by("-start_date").first()
        interest_rate = latest_rate.interest_rate if latest_rate else 0
        r = interest_rate / (12 * 100)
        emi = self.calculate_emi()

        if principal == 0:
            return 0

        if r == 0:
            return math.ceil(principal / emi)

        tenure_remaining = math.log(emi / (emi - (principal * r))) / math.log(1 + r)
        return math.ceil(tenure_remaining)

    def total_interest(self):
        """Calculate total interest payable over loan duration."""
        return round((self.calculate_emi() * self.tenure_months) - self.loan_amount, 2)

    def __str__(self):
        return f"{self.loan_name} - ₹{self.loan_amount}"


class InterestRateHistory(models.Model):
    """Stores historical interest rates for a loan."""

    loan = models.ForeignKey(
        Loan, on_delete=models.CASCADE, related_name="interest_history"
    )
    interest_rate = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Annual interest rate in %"
    )
    start_date = models.DateField(default=date.today)

    class Meta:
        ordering = ["-start_date"]  # Show the latest interest rate first

    def __str__(self):
        return f"{self.interest_rate}% from {self.start_date}"
