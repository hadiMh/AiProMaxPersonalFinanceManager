from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from banking.card_forms import BankCardForm
from banking.models import BankCard
from core.mixins import UserOwnedMixin
from transactions.models import Transaction
from transactions.selectors import card_income_expense


class BankCardListView(UserOwnedMixin, ListView):
    model = BankCard
    template_name = "banking/card_list.html"
    context_object_name = "cards"


class BankCardDetailView(UserOwnedMixin, DetailView):
    model = BankCard
    template_name = "banking/card_detail.html"
    context_object_name = "card"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        card = self.object
        income, expense = card_income_expense(card)
        ctx["income_total"] = income
        ctx["expense_total"] = expense
        ctx["recent_transactions"] = (
            Transaction.objects.filter(user=self.request.user, card=card)
            .select_related("category")
            .order_by("-transaction_date", "-created_at")[:10]
        )
        return ctx


class BankCardCreateView(UserOwnedMixin, CreateView):
    model = BankCard
    form_class = BankCardForm
    template_name = "banking/card_form.html"
    success_url = reverse_lazy("banking:card_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "کارت با موفقیت ایجاد شد.")
        return super().form_valid(form)


class BankCardUpdateView(UserOwnedMixin, UpdateView):
    model = BankCard
    form_class = BankCardForm
    template_name = "banking/card_form.html"
    success_url = reverse_lazy("banking:card_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "کارت با موفقیت ویرایش شد.")
        return super().form_valid(form)
