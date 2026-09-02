from django import forms
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from banking.models import BankCard
from core.forms import JalaliDateField
from transactions.models import CategoryType, Transaction, TransactionCategory, TransactionKind
from transactions.services.setup import create_default_categories


class TransactionForm(forms.ModelForm):
    transaction_date = JalaliDateField(label="تاریخ")
    new_category_name = forms.CharField(
        required=False,
        label="نام دسته‌بندی جدید",
        widget=forms.TextInput(attrs={"placeholder": "نام دسته جدید"}),
    )

    class Meta:
        model = Transaction
        fields = ["card", "category", "amount", "title", "description", "transaction_date"]
        labels = {
            "card": "کارت",
            "category": "دسته‌بندی",
            "amount": "مبلغ",
            "title": "عنوان",
            "description": "توضیحات",
        }

    def __init__(self, *args, user=None, **kwargs):
        if user is None:
            raise ValueError("TransactionForm requires user=")
        self.user = user
        super().__init__(*args, **kwargs)

        cards = BankCard.objects.filter(user=user, is_active=True)
        if self.instance.pk and self.instance.card_id:
            cards = cards | BankCard.objects.filter(pk=self.instance.card_id)
        self.fields["card"].queryset = cards.distinct()

        categories = TransactionCategory.objects.filter(user=user)
        if not categories.exists():
            create_default_categories(user)
            categories = TransactionCategory.objects.filter(user=user)

        category_field = self.fields["category"]
        category_field.queryset = categories
        category_field.required = False
        choices = [("", "---------")]
        income = categories.filter(category_type=CategoryType.INCOME)
        expense = categories.filter(category_type=CategoryType.EXPENSE)
        if income.exists():
            choices.append(
                (CategoryType.INCOME.label, [(c.pk, c.name) for c in income])
            )
        if expense.exists():
            choices.append(
                (CategoryType.EXPENSE.label, [(c.pk, c.name) for c in expense])
            )
        category_field.choices = choices
        category_field.widget.choices = choices

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount == 0:
            raise ValidationError("مبلغ نمی‌تواند صفر باشد.")
        return amount

    def clean(self):
        cleaned = super().clean()
        amount = cleaned.get("amount")
        category = cleaned.get("category")
        new_name = cleaned.get("new_category_name", "").strip()

        if new_name and category:
            raise ValidationError("یا دسته موجود انتخاب کنید یا دسته جدید بسازید، نه هر دو.")

        if amount and amount != 0:
            expected_type = CategoryType.INCOME if amount > 0 else CategoryType.EXPENSE
            if category and category.category_type != expected_type:
                label = "درآمد" if expected_type == CategoryType.INCOME else "هزینه"
                raise ValidationError(f"برای مبلغ {'مثبت' if amount > 0 else 'منفی'} فقط دسته {label} مجاز است.")

        if not category and not new_name:
            raise ValidationError("دسته‌بندی الزامی است.")

        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user = self.user
        instance.transaction_kind = TransactionKind.NORMAL

        new_name = self.cleaned_data.get("new_category_name", "").strip()
        if new_name:
            cat_type = CategoryType.INCOME if instance.amount > 0 else CategoryType.EXPENSE
            try:
                category, _ = TransactionCategory.objects.get_or_create(
                    user=self.user,
                    name=new_name,
                    category_type=cat_type,
                )
            except IntegrityError:
                category = TransactionCategory.objects.get(
                    user=self.user,
                    name=new_name,
                    category_type=cat_type,
                )
            instance.category = category

        if commit:
            instance.save()
        return instance


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
