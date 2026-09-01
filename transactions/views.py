from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from core.mixins import UserOwnedMixin
from transactions.forms import CategoryForm
from transactions.models import TransactionCategory


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
