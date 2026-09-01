from django.core.exceptions import ValidationError
from django.db import models


class CategoryType(models.TextChoices):
    INCOME = "income", "درآمد"
    EXPENSE = "expense", "هزینه"


class TransactionKind(models.TextChoices):
    NORMAL = "normal", "عادی"
    TRANSFER = "transfer", "انتقال"


class TransactionCategory(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="categories",
        verbose_name="کاربر",
    )
    name = models.CharField(max_length=100, verbose_name="نام")
    category_type = models.CharField(
        max_length=10,
        choices=CategoryType.choices,
        verbose_name="نوع",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ["category_type", "name"]
        unique_together = [("user", "name", "category_type")]

    def __str__(self):
        return self.name


class Transaction(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name="کاربر",
    )
    card = models.ForeignKey(
        "banking.BankCard",
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name="کارت",
    )
    category = models.ForeignKey(
        TransactionCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
        verbose_name="دسته‌بندی",
    )
    amount = models.DecimalField(max_digits=15, decimal_places=0, verbose_name="مبلغ")
    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    transaction_date = models.DateField(verbose_name="تاریخ")
    transaction_kind = models.CharField(
        max_length=10,
        choices=TransactionKind.choices,
        default=TransactionKind.NORMAL,
        verbose_name="نوع تراکنش",
    )
    transfer = models.ForeignKey(
        "banking.Transfer",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="transactions",
        verbose_name="انتقال",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "تراکنش"
        verbose_name_plural = "تراکنش‌ها"
        ordering = ["-transaction_date", "-created_at"]

    def __str__(self):
        return f"{self.title}: {self.amount}"

    @property
    def is_income(self) -> bool:
        return self.amount > 0 and self.transaction_kind == TransactionKind.NORMAL

    @property
    def is_expense(self) -> bool:
        return self.amount < 0 and self.transaction_kind == TransactionKind.NORMAL

    def clean(self):
        errors = {}

        if self.amount is None:
            return

        if self.amount == 0:
            errors["amount"] = "مبلغ نمی‌تواند صفر باشد."

        if self.transaction_kind == TransactionKind.NORMAL:
            if not self.category:
                errors["category"] = "دسته‌بندی الزامی است."
            elif self.amount != 0:
                expected = CategoryType.INCOME if self.amount > 0 else CategoryType.EXPENSE
                if self.category.category_type != expected:
                    label = "درآمد" if expected == CategoryType.INCOME else "هزینه"
                    sign = "مثبت" if self.amount > 0 else "منفی"
                    errors["category"] = f"برای مبلغ {sign} فقط دسته {label} مجاز است."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
