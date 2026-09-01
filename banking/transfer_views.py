from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView, FormView, ListView

from banking.forms import TransferForm
from banking.models import Transfer
from banking.services.transfers import create_transfer, delete_transfer, update_transfer
from core.mixins import UserOwnedMixin


class TransferListView(UserOwnedMixin, ListView):
    model = Transfer
    template_name = "banking/transfer_list.html"
    context_object_name = "transfers"

    def get_queryset(self):
        return super().get_queryset().select_related("from_card", "to_card")


class TransferCreateView(UserOwnedMixin, FormView):
    form_class = TransferForm
    template_name = "banking/transfer_form.html"
    success_url = reverse_lazy("banking:transfer_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        try:
            create_transfer(
                user=self.request.user,
                from_card=form.cleaned_data["from_card"],
                to_card=form.cleaned_data["to_card"],
                amount=form.cleaned_data["amount"],
                description=form.cleaned_data["description"],
                transfer_date=form.cleaned_data["transfer_date"],
            )
        except ValueError as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        messages.success(self.request, "انتقال با موفقیت ثبت شد.")
        return redirect(self.success_url)


class TransferUpdateView(UserOwnedMixin, FormView):
    form_class = TransferForm
    template_name = "banking/transfer_form.html"
    success_url = reverse_lazy("banking:transfer_list")

    def dispatch(self, request, *args, **kwargs):
        self.transfer = get_object_or_404(Transfer, pk=kwargs["pk"], user=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs.setdefault("initial", {
            "from_card": self.transfer.from_card,
            "to_card": self.transfer.to_card,
            "amount": self.transfer.amount,
            "description": self.transfer.description,
            "transfer_date": self.transfer.transfer_date,
        })
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["transfer"] = self.transfer
        ctx["is_edit"] = True
        return ctx

    def form_valid(self, form):
        try:
            update_transfer(
                self.transfer,
                from_card=form.cleaned_data["from_card"],
                to_card=form.cleaned_data["to_card"],
                amount=form.cleaned_data["amount"],
                description=form.cleaned_data["description"],
                transfer_date=form.cleaned_data["transfer_date"],
            )
        except ValueError as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        messages.success(self.request, "انتقال با موفقیت ویرایش شد.")
        return redirect(self.success_url)


class TransferDeleteView(UserOwnedMixin, DeleteView):
    model = Transfer
    template_name = "banking/transfer_confirm_delete.html"
    success_url = reverse_lazy("banking:transfer_list")

    def form_valid(self, form):
        delete_transfer(self.object)
        messages.success(self.request, "انتقال با موفقیت حذف شد.")
        return redirect(self.success_url)
