import random
from datetime import timedelta
from decimal import Decimal

import jdatetime
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User
from banking.models import BankCard, Transfer
from banking.services.transfers import create_transfer
from core.dates import current_jalali_month, current_jalali_week, get_jalali_month_range, get_jalali_week_range
from transactions.models import CategoryType, Transaction, TransactionCategory, TransactionKind

RANDOM_SEED = 42
MIN_CARD_BALANCE = Decimal("500_000")

CARDS = [
    ("کارت ملت", "6037994512345678", "ملت"),
    ("کارت ملی", "6037691234567890", "ملی"),
    ("کارت بلو", "6219861234567890", "بلو"),
]

EXPENSE_CATEGORIES = [
    "کافه و رستوران", "رفت و آمد", "خرید روزمره", "قبض و خدمات",
    "خرید لباس", "تفریح", "درمان", "آموزش", "سایر هزینه‌ها",
]

EXPENSE_TITLES = {
    "کافه و رستوران": "کافه و رستوران",
    "رفت و آمد": "رفت و آمد",
    "خرید روزمره": "خرید روزمره",
    "قبض و خدمات": "قبض و خدمات",
    "خرید لباس": "خرید لباس",
    "تفریح": "تفریح",
    "درمان": "درمان",
    "آموزش": "آموزش",
    "سایر هزینه‌ها": "سایر هزینه",
}


def _iter_jalali_months(start_year=1405, start_month=1, end_year=1406, end_month=12):
    year, month = start_year, start_month
    while (year, month) <= (end_year, end_month):
        yield year, month
        month += 1
        if month > 12:
            month = 1
            year += 1


def _days_in_jalali_month(year, month):
    if month == 12:
        next_j = jdatetime.date(year + 1, 1, 1)
    else:
        next_j = jdatetime.date(year, month + 1, 1)
    return (next_j - jdatetime.timedelta(days=1)).day


def _date_on_jalali_day(year, month, day):
    day = min(day, _days_in_jalali_month(year, month))
    return jdatetime.date(year, month, day).togregorian()


def _weeks_overlapping_month(year, month):
    month_start, month_end = get_jalali_month_range(year, month)
    seen = set()
    weeks = []
    for wy in (year - 1, year, year + 1):
        for w in range(1, 54):
            try:
                ws, we = get_jalali_week_range(wy, w)
            except (ValueError, OverflowError):
                continue
            if ws <= month_end and we >= month_start:
                key = ws.isoformat()
                if key in seen:
                    continue
                seen.add(key)
                weeks.append((max(ws, month_start), min(we, month_end)))
    weeks.sort(key=lambda x: x[0])
    return weeks or [(month_start, month_end)]


def _month_date_slots(year, month, count, rng):
    weeks = _weeks_overlapping_month(year, month)
    slots = []
    for i in range(count):
        week = weeks[i % len(weeks)]
        slots.append(_random_day_in_range(rng, week[0], week[1]))
    if _is_current_month(year, month):
        week_start, week_end = _current_week_range()
        slots[0] = _random_day_in_range(rng, week_start, week_end)
        if count > 1:
            slots[1] = _random_day_in_range(rng, week_start, week_end)
    return slots


def _current_week_range():
    wy, ww = current_jalali_week()
    start, end = get_jalali_week_range(wy, ww)
    today = jdatetime.date.today().togregorian()
    return start, min(end, today)


def _random_day_in_range(rng, start, end):
    delta = (end - start).days
    return start + timedelta(days=rng.randint(0, max(delta, 0)))


def _is_current_month(year, month):
    cy, cm = current_jalali_month()
    return year == cy and month == cm


def _get_category(categories, name, cat_type):
    for c in categories:
        if c.name == name and c.category_type == cat_type:
            return c
    raise ValueError(f"Category missing: {name}")


def _refresh_balances(cards, cash):
    return {c.pk: c.balance for c in cards + [cash]}


def _total_balance(balances):
    return sum(balances.values())


def _transfer_from_richest(user, to_card, amount, tx_date, balances, cards, cash):
    if amount <= 0:
        return False
    ordered = sorted(cards + [cash], key=lambda c: balances[c.pk], reverse=True)
    for donor in ordered:
        if donor.pk == to_card.pk:
            continue
        available = balances[donor.pk] - MIN_CARD_BALANCE
        if available <= 0:
            continue
        chunk = min(amount, available)
        create_transfer(
            user=user,
            from_card=donor,
            to_card=to_card,
            amount=chunk,
            description="انتقال خودکار برای پوشش هزینه",
            transfer_date=tx_date,
        )
        balances[donor.pk] -= chunk
        balances[to_card.pk] += chunk
        amount -= chunk
        if amount <= 0:
            return True
    return amount <= 0


def _split_amounts(rng, total, parts, min_part=100_000):
    total = int(total)
    if parts <= 1:
        return [total]
    amounts = []
    remaining = total
    for i in range(parts - 1):
        max_chunk = remaining - min_part * (parts - i - 1)
        if max_chunk < min_part:
            chunk = min_part
        else:
            chunk = rng.randrange(min_part, max_chunk + 1, 10_000)
        amounts.append(chunk)
        remaining -= chunk
    amounts.append(remaining)
    rng.shuffle(amounts)
    return amounts


def _month_totals(rng, year, month, deficit_months):
    income = Decimal(str(rng.randint(25_000_000, 35_000_000)))
    if (year, month) in deficit_months:
        expense = income + Decimal(str(rng.randint(1_000_000, 2_000_000)))
    else:
        expense = income - Decimal(str(rng.randint(1_000_000, 2_000_000)))
    return income, expense


def _create_income_transactions(rng, user, cards, categories, income_total, year, month, balances):
    mellat, melli, blue = cards[0], cards[1], cards[2]
    payloads = []
    weeks = _weeks_overlapping_month(year, month)
    parts = _split_amounts(rng, income_total, max(len(weeks), 3), min_part=1_000_000)
    cards_cycle = [mellat, mellat, blue, melli]
    cats_cycle = ["حقوق", "حقوق", "سرمایه‌گذاری", "پروژه و فریلنس"]
    titles = ["حقوق", "حقوق و مزایا", "سود سرمایه‌گذاری", "درآمد جانبی", "فروش", "درآمد پروژه"]

    for i, amount in enumerate(parts):
        week = weeks[i % len(weeks)]
        tx_date = _random_day_in_range(rng, week[0], week[1])
        if _is_current_month(year, month) and i < 2:
            ws, we = _current_week_range()
            tx_date = _random_day_in_range(rng, ws, we)
        card = cards_cycle[i % len(cards_cycle)]
        cat_name = cats_cycle[i % len(cats_cycle)]
        amount_dec = Decimal(str(amount))
        balances[card.pk] += amount_dec
        payloads.append({
            "user": user,
            "card": card,
            "category": _get_category(categories, cat_name, CategoryType.INCOME),
            "amount": amount_dec,
            "title": titles[i % len(titles)],
            "description": f"درآمد ماه {year}/{month:02d}",
            "transaction_date": tx_date,
            "transaction_kind": TransactionKind.NORMAL,
        })
    return payloads


def _spend_from_card(user, card, amount_dec, tx_date, balances, cards, cash):
    needed = amount_dec + MIN_CARD_BALANCE - balances[card.pk]
    if needed > 0:
        _transfer_from_richest(user, card, needed, tx_date, balances, cards, cash)
    if balances[card.pk] - amount_dec < MIN_CARD_BALANCE:
        mellat = cards[0]
        if card.pk != mellat.pk:
            needed = amount_dec + MIN_CARD_BALANCE - balances[mellat.pk]
            if needed > 0:
                _transfer_from_richest(user, mellat, needed, tx_date, balances, cards, cash)
            card = mellat
    if balances[card.pk] - amount_dec < MIN_CARD_BALANCE:
        return None
    balances[card.pk] -= amount_dec
    return card


def _create_expense_transactions(rng, user, cards, categories, expense_total, year, month, balances, cash):
    mellat, melli, blue = cards[0], cards[1], cards[2]
    payloads = []
    weeks = _weeks_overlapping_month(year, month)
    parts_count = max(len(weeks) * 3, 12)
    amounts = _split_amounts(rng, expense_total, parts_count)
    spend_cards = [melli, mellat, blue, melli, mellat]

    for idx, amount in enumerate(amounts):
        week = weeks[idx % len(weeks)]
        tx_date = _random_day_in_range(rng, week[0], week[1])
        if _is_current_month(year, month) and idx < 3:
            ws, we = _current_week_range()
            tx_date = _random_day_in_range(rng, ws, we)
        amount_dec = Decimal(str(amount))
        cat_name = EXPENSE_CATEGORIES[idx % len(EXPENSE_CATEGORIES)]
        card = spend_cards[idx % len(spend_cards)]
        spent_card = _spend_from_card(user, card, amount_dec, tx_date, balances, cards, cash)
        if spent_card is None:
            spent_card = _spend_from_card(user, mellat, amount_dec, tx_date, balances, cards, cash)
        if spent_card is None:
            raise RuntimeError(f"Cannot spend {amount_dec} in {year}/{month:02d}")

        payloads.append({
            "user": user,
            "card": spent_card,
            "category": _get_category(categories, cat_name, CategoryType.EXPENSE),
            "amount": -amount_dec,
            "title": EXPENSE_TITLES[cat_name],
            "description": f"هزینه ماه {year}/{month:02d}",
            "transaction_date": tx_date,
            "transaction_kind": TransactionKind.NORMAL,
        })

    return payloads


def _verify_month(user, year, month, expected_income, expected_expense):
    month_start, month_end = get_jalali_month_range(year, month)
    from transactions.selectors import total_income, total_expense, transactions_in_range
    qs = transactions_in_range(user, month_start, month_end)
    actual_income = total_income(qs)
    actual_expense = total_expense(qs)
    if actual_income == 0 or actual_expense == 0:
        raise RuntimeError(
            f"Month {year}/{month:02d} incomplete: income={actual_income}, expense={actual_expense}"
        )
    return actual_income, actual_expense


@transaction.atomic
def seed_fixture_data(user: User, *, clear: bool = False) -> dict:
    rng = random.Random(RANDOM_SEED)

    if clear:
        Transaction.objects.filter(user=user).delete()
        Transfer.objects.filter(user=user).delete()
        user.bank_cards.filter(is_cash=False).delete()

    cards = []
    for title, number, bank in CARDS:
        card, _ = BankCard.objects.get_or_create(
            user=user,
            title=title,
            defaults={"card_number": number, "bank_name": bank},
        )
        cards.append(card)

    categories = list(TransactionCategory.objects.filter(user=user))
    cash = user.bank_cards.get(is_cash=True)
    mellat = cards[0]

    all_months = list(_iter_jalali_months())
    deficit_months = set(rng.sample(all_months[3:], 2))

    balances = {c.pk: Decimal("0") for c in cards + [cash]}
    created_normal = 0
    created_transfers = 0
    monthly_summary = []

    for year, month in all_months:
        income_total, expense_total = _month_totals(rng, year, month, deficit_months)

        for payload in _create_income_transactions(
            rng, user, cards, categories, income_total, year, month, balances,
        ):
            Transaction.objects.create(**payload)
            created_normal += 1

        for payload in _create_expense_transactions(
            rng, user, cards, categories, expense_total, year, month, balances, cash,
        ):
            Transaction.objects.create(**payload)
            created_normal += 1

        cards = [BankCard.objects.get(pk=c.pk) for c in cards]
        cash = user.bank_cards.get(is_cash=True)
        balances = _refresh_balances(cards, cash)

        actual_income, actual_expense = _verify_month(user, year, month, income_total, expense_total)

        monthly_summary.append({
            "year": year,
            "month": month,
            "income": actual_income,
            "expense": actual_expense,
            "net": actual_income - actual_expense,
            "deficit": (year, month) in deficit_months,
        })

    final_balances = {c.title: c.balance for c in user.bank_cards.all()}
    negative = [name for name, bal in final_balances.items() if bal < 0]
    if negative:
        raise RuntimeError(f"Cards with negative balance: {', '.join(negative)}")

    total_tx = Transaction.objects.filter(user=user).count()
    avg_income = sum(m["income"] for m in monthly_summary) / len(monthly_summary)
    avg_expense = sum(m["expense"] for m in monthly_summary) / len(monthly_summary)

    return {
        "cards": len(cards),
        "months": len(monthly_summary),
        "deficit_months": [f"{y}/{m:02d}" for y, m in sorted(deficit_months)],
        "avg_monthly_income": avg_income,
        "avg_monthly_expense": avg_expense,
        "normal_transactions": created_normal,
        "transfers": created_transfers,
        "total_transactions": total_tx,
        "balances": final_balances,
    }


class Command(BaseCommand):
    help = "Load monthly fixture from 1405/01 to 1406/12 with ~30M income and ~28M expense per month."

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true")
        parser.add_argument("--username", default="demo")

    def handle(self, *args, **options):
        username = options["username"]
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": f"{username}@example.com", "first_name": "کاربر", "last_name": "نمونه"},
        )
        if created:
            user.set_password("demo1234")
            user.save()
            self.stdout.write(f"User '{username}' created (password: demo1234)")

        stats = seed_fixture_data(user, clear=options["clear"])
        self.stdout.write(self.style.SUCCESS(
            f"Fixture: {stats['months']} months, {stats['total_transactions']} transactions, "
            f"avg income {stats['avg_monthly_income']:,.0f}, avg expense {stats['avg_monthly_expense']:,.0f}"
        ))
        self.stdout.write(f"Deficit months: {', '.join(stats['deficit_months'])}")
        for title, balance in stats["balances"].items():
            self.stdout.write(f"  {title}: {balance:,}")
