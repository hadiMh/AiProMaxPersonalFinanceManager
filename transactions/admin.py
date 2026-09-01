from django.contrib import admin

from transactions.models import Transaction, TransactionCategory


@admin.register(TransactionCategory)
class TransactionCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category_type", "user", "created_at")
    search_fields = ("name", "user__username")
    list_filter = ("category_type",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("title", "amount", "card", "category", "transaction_kind", "transaction_date", "user")
    search_fields = ("title", "description", "user__username")
    list_filter = ("transaction_kind", "transaction_date")
