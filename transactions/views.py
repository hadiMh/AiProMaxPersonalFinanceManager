from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from core.dates import jalali_to_gregorian
from core.forms import JalaliDateField
from core.mixins import UserOwnedMixin
from transactions.forms import CategoryForm, TransactionForm
from transactions.models import CategoryType, Transaction, TransactionCategory, TransactionKind


class TransactionListView(UserOwnedMixin, ListView):
    model = Transaction
    template_name = "transactions/transaction_list.html"
    context_object_name = "transactions"
    paginate_by = 20

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .select_related("card", "category")
            .order_by("-transaction_date", "-created_at")
        )
        user = self.request.user
        params = self.request.GET

        card_id = params.get("card")
        if card_id:
            qs = qs.filter(card_id=card_id, card__user=user)

        category_id = params.get("category")
        if category_id:
            qs = qs.filter(category_id=category_id)

        kind = params.get("kind")
        if kind == "income":
            qs = qs.filter(transaction_kind=TransactionKind.NORMAL, amount__gt=0)
        elif kind == "expense":
            qs = qs.filter(transaction_kind=TransactionKind.NORMAL, amount__lt=0)
        elif kind == "transfer":
            qs = qs.filter(transaction_kind=TransactionKind.TRANSFER)

        search = params.get("q", "").strip()
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))

        date_from = params.get("date_from", "").strip()
        if date_from:
            try:
                qs = qs.filter(transaction_date__gte=jalali_to_gregorian(date_from))
            except ValueError:
                messages.error(self.request, "تاریخ شروع معتبر نیست.")

        date_to = params.get("date_to", "").strip()
        if date_to:
            try:
                qs = qs.filter(transaction_date__lte=jalali_to_gregorian(date_to))
            except ValueError:
                messages.error(self.request, "تاریخ پایان معتبر نیست.")

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["cards"] = user.bank_cards.filter(is_active=True)
        ctx["categories"] = user.categories.all()
        ctx["filters"] = self.request.GET
        return ctx


class TransactionCreateView(UserOwnedMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "transactions/transaction_form.html"
    success_url = reverse_lazy("transactions:list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "تراکنش با موفقیت ثبت شد.")
        return super().form_valid(form)


class TransactionUpdateView(UserOwnedMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "transactions/transaction_form.html"
    success_url = reverse_lazy("transactions:list")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.transaction_kind == TransactionKind.TRANSFER:
            messages.error(request, "تراکنش‌های انتقال را از صفحه انتقال‌ها ویرایش کنید.")
            return self.http_method_not_allowed(request)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "تراکنش با موفقیت ویرایش شد.")
        return super().form_valid(form)


class TransactionDeleteView(UserOwnedMixin, DeleteView):
    model = Transaction
    template_name = "transactions/transaction_confirm_delete.html"
    success_url = reverse_lazy("transactions:list")

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.transaction_kind == TransactionKind.TRANSFER:
            messages.error(request, "تراکنش‌های انتقال را از صفحه انتقال‌ها حذف کنید.")
            return self.http_method_not_allowed(request)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "تراکنش با موفقیت حذف شد.")
        return super().form_valid(form)


class CategoryListView(UserOwnedMixin, ListView):
    model = TransactionCategory
    template_name = "transactions/category_list.html"
    context_object_name = "categories"


class CategoryCreateView(UserOwnedMixin, CreateView):
    model = TransactionCategory
    form_class = CategoryForm
    template_name = "transactions/category_form.html"
    success_url = reverse_lazy("transactions:category_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "دسته‌بندی با موفقیت ایجاد شد.")
        return super().form_valid(form)


class CategoryUpdateView(UserOwnedMixin, UpdateView):
    model = TransactionCategory
    form_class = CategoryForm
    template_name = "transactions/category_form.html"
    success_url = reverse_lazy("transactions:category_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "دسته‌بندی با موفقیت ویرایش شد.")
        return super().form_valid(form)


class CategoryDeleteView(UserOwnedMixin, DeleteView):
    model = TransactionCategory
    template_name = "transactions/category_confirm_delete.html"
    success_url = reverse_lazy("transactions:category_list")

    def form_valid(self, form):
        messages.success(self.request, "دسته‌بندی با موفقیت حذف شد.")
        return super().form_valid(form)


def categories_by_type(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    cat_type = request.GET.get("type")
    if cat_type not in (CategoryType.INCOME, CategoryType.EXPENSE):
        return JsonResponse({"categories": []})
    cats = TransactionCategory.objects.filter(user=request.user, category_type=cat_type)
    return JsonResponse({
        "categories": [{"id": c.id, "name": c.name} for c in cats],
    })
