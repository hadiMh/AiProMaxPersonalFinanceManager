from django.contrib import admin

from banking.models import BankCard


@admin.register(BankCard)
class BankCardAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "bank_name", "is_cash", "is_active", "created_at")
    search_fields = ("title", "card_number", "bank_name", "user__username")
    list_filter = ("is_cash", "is_active", "bank_name")
