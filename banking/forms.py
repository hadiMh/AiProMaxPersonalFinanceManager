from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError

from banking.models import BankCard
from banking.services.transfers import _available_balance
from core.forms import JalaliDateField


class TransferForm(forms.Form):
    from_card = forms.ModelChoiceField(queryset=BankCard.objects.none(), label="از کارت")
    to_card = forms.ModelChoiceField(queryset=BankCard.objects.none(), label="به کارت")
    amount = forms.DecimalField(max_digits=15, decimal_places=0, label="مبلغ")
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}), label="توضیحات")
    transfer_date = JalaliDateField(label="تاریخ انتقال")

    def __init__(self, *args, user=None, transfer=None, **kwargs):
        self.user = user
        self.transfer = transfer
        super().__init__(*args, **kwargs)
        if user:
            cards = BankCard.objects.filter(user=user, is_active=True)
            if transfer:
                cards = cards | BankCard.objects.filter(
                    pk__in=[transfer.from_card_id, transfer.to_card_id]
                )
            cards = cards.distinct()
            self.fields["from_card"].queryset = cards
            self.fields["to_card"].queryset = cards

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= Decimal("0"):
            raise ValidationError("مبلغ انتقال باید بزرگ‌تر از صفر باشد.")
        return amount

    def clean(self):
        cleaned = super().clean()
        from_card = cleaned.get("from_card")
        to_card = cleaned.get("to_card")
        amount = cleaned.get("amount")
        if from_card and to_card and from_card == to_card:
            raise ValidationError("کارت مبدا و مقصد نمی‌توانند یکسان باشند.")
        if from_card and amount:
            if not from_card.is_active:
                raise ValidationError("کارت مبدا غیرفعال است.")
            exclude = None
            if self.transfer and self.transfer.outgoing_transaction:
                exclude = self.transfer.outgoing_transaction
            available = _available_balance(from_card, exclude_transaction=exclude)
            if available < amount:
                raise ValidationError("موجودی کارت مبدا کافی نیست.")
        if to_card and not to_card.is_active:
            raise ValidationError("کارت مقصد غیرفعال است.")
        return cleaned
