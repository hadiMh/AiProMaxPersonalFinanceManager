from django.contrib import admin

from banking.models import BankCard, Transfer


@admin.register(BankCard)
class BankCardAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "bank_name", "is_cash", "is_active", "created_at")
    search_fields = ("title", "card_number", "bank_name", "user__username")
    list_filter = ("is_cash", "is_active", "bank_name")


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ("from_card", "to_card", "amount", "transfer_date", "user", "created_at")
    search_fields = ("description", "from_card__title", "to_card__title", "user__username")
    list_filter = ("transfer_date",)
