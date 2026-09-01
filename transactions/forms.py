from django import forms

from transactions.models import TransactionCategory


class CategoryForm(forms.ModelForm):
    class Meta:
        model = TransactionCategory
        fields = ["name", "category_type"]
        labels = {"name": "نام", "category_type": "نوع"}

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user = self.user
        if commit:
            instance.save()
        return instance
