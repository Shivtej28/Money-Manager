from django import forms
from .models import Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name", "parent", "category_type")
        labels = {"name": "Category Name", "parent": "Parent Category (Optional)"}
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Food", "class": "form-control"}
            ),
            "parent": forms.Select(attrs={"class": "form-control"}),
            "category_type": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["parent"].queryset = Category.objects.filter(parent__isnull=True)
