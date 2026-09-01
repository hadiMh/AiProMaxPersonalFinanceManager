from banking.models import BankCard


def create_cash_card(user):
    if BankCard.objects.filter(user=user, is_cash=True).exists():
        return
    BankCard.objects.create(
        user=user,
        title="نقدی",
        is_cash=True,
        bank_name="نقدی",
    )
