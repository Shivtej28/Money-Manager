from django import forms
from .models import InterestRateHistory, Loan


class LoanForm(forms.ModelForm):
    """Form for adding and updating loans."""

    class Meta:
        model = Loan
        fields = [
            "loan_name",
            "loan_amount",
            "interest_rate",
            "tenure_months",
            "category",
            "start_date",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "category": forms.Select(attrs={"class": "form-control"}),
        }


class InterestRateUpdateForm(forms.ModelForm):
    """Form for updating the interest rate of a loan."""

    class Meta:
        model = InterestRateHistory
        fields = ["interest_rate", "start_date"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
        }
