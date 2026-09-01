from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from banking.models import BankCard, Transfer
from banking.services.transfers import create_transfer, delete_transfer, update_transfer
from core.dates import gregorian_to_jalali, jalali_to_gregorian
from transactions.models import CategoryType, Transaction, TransactionCategory, TransactionKind
from transactions.selectors import category_breakdown, total_expense, total_income, transactions_in_range

User = get_user_model()


class FinanceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.other = User.objects.create_user(username="other", password="otherpass123")
        self.cash = self.user.bank_cards.get(is_cash=True)
        self.card = BankCard.objects.create(
            user=self.user,
            title="کارت تست",
            card_number="6037991234567890",
            bank_name="ملت",
        )
        self.other_card = BankCard.objects.create(
            user=self.other,
            title="کارت دیگر",
            card_number="6037698765432101",
            bank_name="ملی",
        )
        self.card2 = BankCard.objects.create(
            user=self.user,
            title="کارت دوم",
            card_number="5022291122334455",
            bank_name="پاسارگاد",
        )
        self.income_cat = TransactionCategory.objects.get(user=self.user, name="حقوق")
        self.expense_cat = TransactionCategory.objects.get(user=self.user, name="کافه و رستوران")

    def test_balance_starts_at_zero(self):
        self.assertEqual(self.card.balance, Decimal("0"))

    def test_positive_transaction_increases_balance(self):
        Transaction.objects.create(
            user=self.user, card=self.card, category=self.income_cat,
            amount=Decimal("1000000"), title="درآمد", transaction_date=date.today(),
        )
        self.assertEqual(self.card.balance, Decimal("1000000"))

    def test_negative_transaction_decreases_balance(self):
        Transaction.objects.create(
            user=self.user, card=self.card, category=self.expense_cat,
            amount=Decimal("-500000"), title="هزینه", transaction_date=date.today(),
        )
        self.assertEqual(self.card.balance, Decimal("-500000"))

    def test_zero_transaction_invalid(self):
        from django.core.exceptions import ValidationError
        from transactions.forms import TransactionForm
        form = TransactionForm(
            data={
                "card": self.card.pk, "category": self.expense_cat.pk,
                "amount": "0", "title": "صفر", "transaction_date": "1404/01/01",
            },
            user=self.user,
        )
        self.assertFalse(form.is_valid())

    def test_transfer_decreases_source_balance(self):
        Transaction.objects.create(
            user=self.user, card=self.card, category=self.income_cat,
            amount=Decimal("10000000"), title="درآمد", transaction_date=date.today(),
        )
        create_transfer(
            user=self.user, from_card=self.card, to_card=self.card2,
            amount=Decimal("3000000"), description="", transfer_date=date.today(),
        )
        self.assertEqual(self.card.balance, Decimal("7000000"))

    def test_transfer_increases_destination_balance(self):
        Transaction.objects.create(
            user=self.user, card=self.card, category=self.income_cat,
            amount=Decimal("10000000"), title="درآمد", transaction_date=date.today(),
        )
        create_transfer(
            user=self.user, from_card=self.card, to_card=self.card2,
            amount=Decimal("3000000"), description="", transfer_date=date.today(),
        )
        self.assertEqual(self.card2.balance, Decimal("3000000"))

    def test_transfer_not_income(self):
        create_transfer(
            user=self.user, from_card=self.card, to_card=self.card2,
            amount=Decimal("5000000"), description="", transfer_date=date.today(),
        )
        qs = transactions_in_range(self.user, date(2000, 1, 1), date(2100, 1, 1))
        self.assertEqual(total_income(qs), Decimal("0"))

    def test_transfer_not_expense(self):
        create_transfer(
            user=self.user, from_card=self.card, to_card=self.card2,
            amount=Decimal("5000000"), description="", transfer_date=date.today(),
        )
        qs = transactions_in_range(self.user, date(2000, 1, 1), date(2100, 1, 1))
        self.assertEqual(total_expense(qs), Decimal("0"))

    def test_transfer_not_in_category_reports(self):
        create_transfer(
            user=self.user, from_card=self.card, to_card=self.card2,
            amount=Decimal("5000000"), description="", transfer_date=date.today(),
        )
        qs = transactions_in_range(self.user, date(2000, 1, 1), date(2100, 1, 1))
        self.assertEqual(category_breakdown(qs, CategoryType.EXPENSE), [])
        self.assertEqual(category_breakdown(qs, CategoryType.INCOME), [])

    def test_transfer_edit_syncs_transactions(self):
        transfer = create_transfer(
            user=self.user, from_card=self.card, to_card=self.card2,
            amount=Decimal("5000000"), description="اول", transfer_date=date.today(),
        )
        update_transfer(
            transfer, from_card=self.card, to_card=self.card2,
            amount=Decimal("8000000"), description="ویرایش", transfer_date=date.today(),
        )
        transfer.refresh_from_db()
        self.assertEqual(transfer.amount, Decimal("8000000"))
        self.assertEqual(transfer.outgoing_transaction.amount, Decimal("-8000000"))
        self.assertEqual(transfer.incoming_transaction.amount, Decimal("8000000"))

    def test_transfer_delete_cleans_transactions(self):
        transfer = create_transfer(
            user=self.user, from_card=self.card, to_card=self.card2,
            amount=Decimal("5000000"), description="", transfer_date=date.today(),
        )
        out_id = transfer.outgoing_transaction_id
        in_id = transfer.incoming_transaction_id
        delete_transfer(transfer)
        self.assertFalse(Transfer.objects.filter(pk=transfer.pk).exists())
        self.assertFalse(Transaction.objects.filter(pk__in=[out_id, in_id]).exists())

    def test_user_isolation(self):
        client = Client()
        client.login(username="testuser", password="testpass123")
        url = reverse("banking:card_detail", args=[self.other_card.pk])
        response = client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_category_validation(self):
        from transactions.forms import TransactionForm
        form = TransactionForm(
            data={
                "card": self.card.pk, "category": self.expense_cat.pk,
                "amount": "1000000", "title": "اشتباه", "transaction_date": "1404/06/01",
            },
            user=self.user,
        )
        self.assertFalse(form.is_valid())

    def test_jalali_date_conversion(self):
        g = date(2025, 9, 1)
        j = gregorian_to_jalali(g)
        self.assertEqual(jalali_to_gregorian(j), g)

    def test_unauthorized_access(self):
        client = Client()
        response = client.get(reverse("dashboard:weekly"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_cash_card_created_on_signup(self):
        self.assertTrue(BankCard.objects.filter(user=self.user, is_cash=True, title="نقدی").exists())

    def test_default_categories_created(self):
        self.assertTrue(TransactionCategory.objects.filter(user=self.user).count() >= 18)

    def test_zero_transaction_rejected_at_model(self):
        from django.core.exceptions import ValidationError

        tx = Transaction(
            user=self.user,
            card=self.card,
            category=self.expense_cat,
            amount=Decimal("0"),
            title="صفر",
            transaction_date=date.today(),
        )
        with self.assertRaises(ValidationError):
            tx.save()

    def test_edit_transaction_updates_balance(self):
        tx = Transaction.objects.create(
            user=self.user,
            card=self.card,
            category=self.income_cat,
            amount=Decimal("10000000"),
            title="درآمد",
            transaction_date=date.today(),
        )
        self.assertEqual(self.card.balance, Decimal("10000000"))
        tx.amount = Decimal("5000000")
        tx.save()
        self.assertEqual(self.card.balance, Decimal("5000000"))

    def test_edit_transaction_card_updates_balances(self):
        tx = Transaction.objects.create(
            user=self.user,
            card=self.card,
            category=self.income_cat,
            amount=Decimal("10000000"),
            title="درآمد",
            transaction_date=date.today(),
        )
        tx.card = self.card2
        tx.save()
        self.assertEqual(self.card.balance, Decimal("0"))
        self.assertEqual(self.card2.balance, Decimal("10000000"))

    def test_delete_transaction_updates_balance(self):
        tx = Transaction.objects.create(
            user=self.user,
            card=self.card,
            category=self.income_cat,
            amount=Decimal("10000000"),
            title="درآمد",
            transaction_date=date.today(),
        )
        self.assertEqual(self.card.balance, Decimal("10000000"))
        tx.delete()
        self.assertEqual(self.card.balance, Decimal("0"))

    def test_cash_transfer_balances_and_reports(self):
        Transaction.objects.create(
            user=self.user,
            card=self.card,
            category=self.income_cat,
            amount=Decimal("10000000"),
            title="درآمد",
            transaction_date=date.today(),
        )
        create_transfer(
            user=self.user,
            from_card=self.card,
            to_card=self.cash,
            amount=Decimal("1000000"),
            description="برداشت نقدی",
            transfer_date=date.today(),
        )
        self.assertEqual(self.card.balance, Decimal("9000000"))
        self.assertEqual(self.cash.balance, Decimal("1000000"))
        qs = transactions_in_range(self.user, date(2000, 1, 1), date(2100, 1, 1))
        self.assertEqual(total_income(qs), Decimal("10000000"))
        self.assertEqual(total_expense(qs), Decimal("0"))

    def test_cross_user_card_rejected_on_transaction_create(self):
        client = Client()
        client.login(username="testuser", password="testpass123")
        other_cat = TransactionCategory.objects.get(user=self.other, name="حقوق")
        response = client.post(
            reverse("transactions:create"),
            {
                "card": self.other_card.pk,
                "category": other_cat.pk,
                "amount": "1000000",
                "title": "نفوذ",
                "transaction_date": "1404/06/01",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Transaction.objects.filter(title="نفوذ").exists())

    def test_cross_user_category_rejected_on_transaction_create(self):
        client = Client()
        client.login(username="testuser", password="testpass123")
        other_cat = TransactionCategory.objects.get(user=self.other, name="حقوق")
        response = client.post(
            reverse("transactions:create"),
            {
                "card": self.card.pk,
                "category": other_cat.pk,
                "amount": "1000000",
                "title": "نفوذ",
                "transaction_date": "1404/06/01",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Transaction.objects.filter(title="نفوذ").exists())

    def test_cross_user_transfer_rejected(self):
        client = Client()
        client.login(username="testuser", password="testpass123")
        response = client.post(
            reverse("banking:transfer_create"),
            {
                "from_card": self.other_card.pk,
                "to_card": self.card.pk,
                "amount": "1000000",
                "description": "نفوذ",
                "transfer_date": "1404/06/01",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Transfer.objects.filter(description="نفوذ").exists())

    def test_duplicate_cash_card_rejected(self):
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            BankCard.objects.create(
                user=self.user,
                title="نقدی دوم",
                is_cash=True,
                bank_name="نقدی",
            )

    def test_other_user_can_have_own_cash_card(self):
        self.assertTrue(BankCard.objects.filter(user=self.other, is_cash=True).exists())
