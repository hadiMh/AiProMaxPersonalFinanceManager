from django import forms

from banking.models import BankCard
from core.validators import validate_card_number


class BankCardForm(forms.ModelForm):
    class Meta:
        model = BankCard
        fields = ["title", "card_number", "bank_name", "account_number", "is_active"]
        labels = {
            "title": "عنوان",
            "card_number": "شماره کارت",
            "bank_name": "نام بانک",
            "account_number": "شماره حساب (اختیاری)",
            "is_active": "فعال",
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.is_cash:
            self.fields["card_number"].required = False
            self.fields["card_number"].disabled = True
            self.fields["bank_name"].disabled = True

    def clean_card_number(self):
        value = self.cleaned_data.get("card_number")
        if self.instance and self.instance.is_cash:
            return None
        if value:
            validate_card_number(value)
            return value.replace(" ", "").replace("-", "")
        raise forms.ValidationError("شماره کارت الزامی است.")

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user = self.user
        if commit:
            instance.save()
        return instance
