import json

from django.contrib import messages
from django.views.generic import TemplateView

from banking.models import BankCard
from core.dates import (
    current_jalali_month,
    current_jalali_week,
    get_jalali_month_range,
    get_jalali_week_range,
    gregorian_to_jalali,
    jalali_month_choices,
    jalali_month_name,
    jalali_to_gregorian,
    jalali_week_for_gregorian,
)
from core.mixins import UserOwnedMixin
from transactions.models import Transaction
from transactions.selectors import (
    category_breakdown,
    highest_category,
    total_expense,
    total_income,
    transactions_in_range,
)


class WeeklyDashboardView(UserOwnedMixin, TemplateView):
    template_name = "dashboard/weekly.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        default_year, default_week = current_jalali_week()
        week_date = self.request.GET.get("week_date", "").strip()

        if week_date:
            try:
                ref_date = jalali_to_gregorian(week_date)
                year, week = jalali_week_for_gregorian(ref_date)
            except ValueError:
                messages.error(self.request, "تاریخ هفته معتبر نیست.")
                year, week = default_year, default_week
                week_date = gregorian_to_jalali(get_jalali_week_range(default_year, default_week)[0])
        else:
            try:
                year = int(self.request.GET.get("year", default_year))
                week = int(self.request.GET.get("week", default_week))
                if week < 1 or week > 53:
                    raise ValueError
            except (TypeError, ValueError):
                messages.error(self.request, "سال یا شماره هفته معتبر نیست.")
                year, week = default_year, default_week
            week_date = gregorian_to_jalali(get_jalali_week_range(year, week)[0])

        start, end = get_jalali_week_range(year, week)
        qs = transactions_in_range(user, start, end)
        expense_breakdown = category_breakdown(qs, "expense")
        income_breakdown = category_breakdown(qs, "income")

        ctx["year"] = year
        ctx["week"] = week
        ctx["week_date"] = week_date
        ctx["start_date"] = start
        ctx["end_date"] = end
        ctx["total_income"] = total_income(qs)
        ctx["total_expense"] = total_expense(qs)
        ctx["net"] = ctx["total_income"] - ctx["total_expense"]
        ctx["transaction_count"] = qs.count()
        ctx["expense_breakdown"] = expense_breakdown
        ctx["income_breakdown"] = income_breakdown
        ctx["highest_expense_category"] = highest_category(expense_breakdown)
        ctx["highest_income_category"] = highest_category(income_breakdown)
        ctx["expense_chart"] = json.dumps(
            [{"label": r["name"], "value": float(r["total"])} for r in expense_breakdown]
        )
        ctx["income_chart"] = json.dumps(
            [{"label": r["name"], "value": float(r["total"])} for r in income_breakdown]
        )
        ctx["recent_transactions"] = (
            Transaction.objects.filter(user=user)
            .select_related("card", "category")
            .order_by("-transaction_date", "-created_at")[:10]
        )
        ctx["cards"] = BankCard.objects.filter(user=user)
        ctx["total_balance"] = sum(c.balance for c in ctx["cards"])
        return ctx


class MonthlyDashboardView(UserOwnedMixin, TemplateView):
    template_name = "dashboard/monthly.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        default_year, default_month = current_jalali_month()

        try:
            year = int(self.request.GET.get("year", default_year))
            month = int(self.request.GET.get("month", default_month))
            if month < 1 or month > 12:
                raise ValueError
        except (TypeError, ValueError):
            messages.error(self.request, "سال یا ماه معتبر نیست.")
            year, month = default_year, default_month

        start, end = get_jalali_month_range(year, month)
        qs = transactions_in_range(user, start, end)
        expense_breakdown = category_breakdown(qs, "expense")
        income_breakdown = category_breakdown(qs, "income")

        ctx["year"] = year
        ctx["month"] = month
        ctx["month_name"] = jalali_month_name(month)
        ctx["month_choices"] = jalali_month_choices()
        ctx["start_date"] = start
        ctx["end_date"] = end
        ctx["total_income"] = total_income(qs)
        ctx["total_expense"] = total_expense(qs)
        ctx["net"] = ctx["total_income"] - ctx["total_expense"]
        ctx["transaction_count"] = qs.count()
        ctx["expense_breakdown"] = expense_breakdown
        ctx["income_breakdown"] = income_breakdown
        ctx["highest_expense_category"] = highest_category(expense_breakdown)
        ctx["highest_income_category"] = highest_category(income_breakdown)
        ctx["expense_chart"] = json.dumps(
            [{"label": r["name"], "value": float(r["total"])} for r in expense_breakdown]
        )
        ctx["income_chart"] = json.dumps(
            [{"label": r["name"], "value": float(r["total"])} for r in income_breakdown]
        )
        ctx["cards"] = BankCard.objects.filter(user=user)
        ctx["total_balance"] = sum(c.balance for c in ctx["cards"])
        return ctx
