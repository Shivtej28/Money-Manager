from django import forms
from .models import Banks

BANK_TYPES = [
    ("savings", "Savings Account"),
    ("current", "Current Account"),
    ("fixed", "Fixed Deposit"),
]


class BankForm(forms.ModelForm):
    class Meta:
        model = Banks
        fields = ("name", "balance", "account_type")
        labels = {
            "name": "Bank Name",
            "balance": "Current Balance",
            "account_type": "Account Type",
        }
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "HDFC Bank", "class": "form-control"}
            ),
            "balance": forms.NumberInput(
                attrs={"placeholder": "1678", "class": "form-control"}
            ),
            "account_type": forms.Select(
                attrs={
                    "placeholder": "HDFC Bank",
                    "class": "form-control",
                },
                choices=BANK_TYPES,
            ),
        }
