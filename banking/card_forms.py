from django import forms
from django.core.exceptions import ValidationError

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
            self.fields["is_active"].disabled = True
            self.fields["is_active"].initial = True

    def clean_card_number(self):
        value = self.cleaned_data.get("card_number")
        if self.instance and self.instance.is_cash:
            return None
        if value:
            validate_card_number(value)
            normalized = value.replace(" ", "").replace("-", "")
            duplicate = BankCard.objects.filter(
                user=self.user,
                card_number=normalized,
            ).exclude(pk=self.instance.pk if self.instance.pk else None)
            if duplicate.exists():
                raise forms.ValidationError("این شماره کارت قبلاً ثبت شده است.")
            return normalized
        raise forms.ValidationError("شماره کارت الزامی است.")

    def clean(self):
        cleaned = super().clean()
        if self.instance and self.instance.is_cash:
            cleaned["is_active"] = True
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user = self.user
        if instance.is_cash:
            instance.is_active = True
        if commit:
            instance.save()
        return instance
