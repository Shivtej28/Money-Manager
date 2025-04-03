from django import forms

from .models import Transaction
from banks.models import Banks
from categories.models import Category


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            "bank",
            "description",
            "transaction_date",
            "subcategory",
            "amount",
        ]
        widgets = {
            "transaction_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "amount": forms.NumberInput(attrs={"class": "form-control"}),
            "subcategory": forms.Select(attrs={"class": "form-control"}),
            "bank": forms.Select(attrs={"class": "form-control"}),  # Add bank selection
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        print(user)
        if user is not None:
            self.fields["bank"].queryset = Banks.objects.filter(user=user)

            self.fields["subcategory"].queryset = Category.objects.filter(
                user=user, parent__isnull=False
            )
