from django import forms
from django.core.exceptions import ValidationError

from banking.models import BankCard
from core.forms import JalaliDateField
from transactions.models import CategoryType, Transaction, TransactionCategory, TransactionKind


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
        self.user = user
        super().__init__(*args, **kwargs)
        if user:
            self.fields["card"].queryset = BankCard.objects.filter(user=user, is_active=True)
            categories = TransactionCategory.objects.filter(user=user)
            category_field = self.fields["category"]
            category_field.queryset = categories
            category_field.required = False
            category_field.choices = [("", "---------")]
            income = categories.filter(category_type=CategoryType.INCOME)
            expense = categories.filter(category_type=CategoryType.EXPENSE)
            if income.exists():
                category_field.choices.append(
                    (CategoryType.INCOME.label, [(c.pk, c.name) for c in income])
                )
            if expense.exists():
                category_field.choices.append(
                    (CategoryType.EXPENSE.label, [(c.pk, c.name) for c in expense])
                )

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
            category, _ = TransactionCategory.objects.get_or_create(
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
