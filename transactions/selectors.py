from decimal import Decimal

from django.db.models import Count, Sum

from transactions.models import CategoryType, Transaction, TransactionKind


def normal_transactions(user):
    return Transaction.objects.filter(user=user, transaction_kind=TransactionKind.NORMAL)


def transactions_in_range(user, start_date, end_date):
    return normal_transactions(user).filter(
        transaction_date__gte=start_date,
        transaction_date__lte=end_date,
    )


def total_income(qs) -> Decimal:
    return qs.filter(amount__gt=0).aggregate(total=Sum("amount"))["total"] or Decimal("0")


def total_expense(qs) -> Decimal:
    total = qs.filter(amount__lt=0).aggregate(total=Sum("amount"))["total"] or Decimal("0")
    return abs(total)


def category_breakdown(qs, category_type: str):
    filtered = qs.filter(amount__gt=0) if category_type == CategoryType.INCOME else qs.filter(amount__lt=0)
    rows = (
        filtered.values("category__name", "category__id")
        .annotate(total=Sum("amount"), count=Count("id"))
        .order_by("-total")
    )
    result = []
    for row in rows:
        total = row["total"] or Decimal("0")
        if category_type == CategoryType.EXPENSE:
            total = abs(total)
        result.append({
            "name": row["category__name"] or "بدون دسته",
            "total": total,
            "count": row["count"],
        })
    return result


def highest_category(breakdown: list) -> dict | None:
    return breakdown[0] if breakdown else None


def card_income_expense(card):
    qs = card.transactions.filter(transaction_kind=TransactionKind.NORMAL)
    income = qs.filter(amount__gt=0).aggregate(total=Sum("amount"))["total"] or Decimal("0")
    expense_raw = qs.filter(amount__lt=0).aggregate(total=Sum("amount"))["total"] or Decimal("0")
    return income, abs(expense_raw)
