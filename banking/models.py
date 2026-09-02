from decimal import Decimal

from django.db import models
from django.db.models import Q, Sum

from core.validators import mask_card_number, validate_card_number


class BankCard(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="bank_cards",
        verbose_name="کاربر",
    )
    title = models.CharField(max_length=100, verbose_name="عنوان")
    card_number = models.CharField(
        max_length=16,
        blank=True,
        null=True,
        validators=[validate_card_number],
        verbose_name="شماره کارت",
    )
    bank_name = models.CharField(max_length=100, blank=True, verbose_name="نام بانک")
    account_number = models.CharField(max_length=50, blank=True, verbose_name="شماره حساب (اختیاری)")
    is_cash = models.BooleanField(default=False, verbose_name="نقدی")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "کارت"
        verbose_name_plural = "کارت‌ها"
        ordering = ["-is_cash", "title"]
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(is_cash=True),
                name="unique_cash_card_per_user",
            ),
            models.UniqueConstraint(
                fields=["user", "card_number"],
                condition=Q(card_number__isnull=False) & ~Q(card_number=""),
                name="unique_card_number_per_user",
            ),
        ]

    def __str__(self):
        return self.title

    @property
    def balance(self) -> Decimal:
        total = self.transactions.aggregate(total=Sum("amount"))["total"]
        return total or Decimal("0")

    @property
    def masked_card_number(self) -> str:
        return mask_card_number(self.card_number)

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.is_cash:
            if self.card_number:
                raise ValidationError({"card_number": "کارت نقدی نیازی به شماره کارت ندارد."})
        else:
            if not self.card_number:
                raise ValidationError({"card_number": "شماره کارت الزامی است."})


class Transfer(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="transfers",
        verbose_name="کاربر",
    )
    from_card = models.ForeignKey(
        BankCard,
        on_delete=models.CASCADE,
        related_name="outgoing_transfers",
        verbose_name="از کارت",
    )
    to_card = models.ForeignKey(
        BankCard,
        on_delete=models.CASCADE,
        related_name="incoming_transfers",
        verbose_name="به کارت",
    )
    amount = models.DecimalField(max_digits=15, decimal_places=0, verbose_name="مبلغ")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    transfer_date = models.DateField(verbose_name="تاریخ انتقال")
    outgoing_transaction = models.OneToOneField(
        "transactions.Transaction",
        on_delete=models.CASCADE,
        related_name="outgoing_transfer",
        null=True,
        blank=True,
    )
    incoming_transaction = models.OneToOneField(
        "transactions.Transaction",
        on_delete=models.CASCADE,
        related_name="incoming_transfer",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "انتقال"
        verbose_name_plural = "انتقال‌ها"
        ordering = ["-transfer_date", "-created_at"]

    def __str__(self):
        return f"{self.from_card} → {self.to_card}: {self.amount}"
