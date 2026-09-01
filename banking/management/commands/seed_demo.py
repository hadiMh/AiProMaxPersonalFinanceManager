from datetime import timedelta
from decimal import Decimal

import jdatetime
from django.core.management.base import BaseCommand

from accounts.models import User
from banking.models import BankCard
from banking.services.transfers import create_transfer
from transactions.models import CategoryType, Transaction, TransactionCategory, TransactionKind


class Command(BaseCommand):
    help = "Create demo user with sample cards, transactions, and transfers."

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username="demo",
            defaults={"email": "demo@example.com", "first_name": "کاربر", "last_name": "نمونه"},
        )
        if created:
            user.set_password("demo1234")
            user.save()
            self.stdout.write("Demo user created (username: demo, password: demo1234)")
        else:
            self.stdout.write("Demo user already exists — adding more data.")

        cash = user.bank_cards.get(is_cash=True)
        cards_data = [
            ("کارت ملت", "6037991234567890", "ملت"),
            ("کارت ملی", "6037698765432101", "ملی"),
            ("کارت پاسارگاد", "5022291122334455", "پاسارگاد"),
        ]
        cards = []
        for title, number, bank in cards_data:
            card, _ = BankCard.objects.get_or_create(
                user=user,
                title=title,
                defaults={"card_number": number, "bank_name": bank},
            )
            cards.append(card)

        salary_cat = TransactionCategory.objects.get(user=user, name="حقوق", category_type=CategoryType.INCOME)
        cafe_cat = TransactionCategory.objects.get(user=user, name="کافه و رستوران", category_type=CategoryType.EXPENSE)
        transport_cat = TransactionCategory.objects.get(user=user, name="رفت و آمد", category_type=CategoryType.EXPENSE)
        shopping_cat = TransactionCategory.objects.get(user=user, name="خرید روزمره", category_type=CategoryType.EXPENSE)

        today = jdatetime.date.today()
        dates = [today.togregorian() - timedelta(days=i * 3) for i in range(10)]

        samples = [
            (cards[0], salary_cat, Decimal("50000000"), "حقوق ماهانه", dates[0]),
            (cards[0], cafe_cat, Decimal("-500000"), "کافه", dates[1]),
            (cards[0], transport_cat, Decimal("-300000"), "مترو", dates[2]),
            (cards[1], shopping_cat, Decimal("-1200000"), "خرید سوپرمارکت", dates[3]),
            (cards[1], cafe_cat, Decimal("-250000"), "ناهار", dates[4]),
            (cards[2], transport_cat, Decimal("-150000"), "تاکسی", dates[5]),
            (cards[0], shopping_cat, Decimal("-800000"), "خرید روزمره", dates[6]),
        ]

        for card, category, amount, title, tx_date in samples:
            if not Transaction.objects.filter(user=user, title=title, transaction_date=tx_date).exists():
                Transaction.objects.create(
                    user=user,
                    card=card,
                    category=category,
                    amount=amount,
                    title=title,
                    transaction_date=tx_date,
                    transaction_kind=TransactionKind.NORMAL,
                )

        if not user.transfers.exists():
            create_transfer(
                user=user,
                from_card=cards[0],
                to_card=cash,
                amount=Decimal("1000000"),
                description="برداشت نقدی",
                transfer_date=dates[7],
            )
            create_transfer(
                user=user,
                from_card=cards[0],
                to_card=cards[1],
                amount=Decimal("5000000"),
                description="انتقال بین کارت‌ها",
                transfer_date=dates[8],
            )

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
