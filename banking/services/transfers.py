from decimal import Decimal

from django.db import transaction

from banking.models import Transfer
from transactions.models import Transaction, TransactionKind


def _validate_transfer_cards(from_card, to_card, user):
    if from_card == to_card:
        raise ValueError("کارت مبدا و مقصد نمی‌توانند یکسان باشند.")
    if from_card.user != user or to_card.user != user:
        raise ValueError("هر دو کارت باید متعلق به شما باشند.")
    if not from_card.is_active:
        raise ValueError("کارت مبدا غیرفعال است.")
    if not to_card.is_active:
        raise ValueError("کارت مقصد غیرفعال است.")


def _available_balance(card, exclude_transaction=None) -> Decimal:
    balance = card.balance
    if exclude_transaction and exclude_transaction.card_id == card.pk:
        balance -= exclude_transaction.amount
    return balance


def _validate_sufficient_balance(from_card, amount, exclude_transaction=None):
    available = _available_balance(from_card, exclude_transaction)
    if available < amount:
        raise ValueError("موجودی کارت مبدا کافی نیست.")


def _create_transfer_transactions(transfer, *, from_card, to_card, amount, description, transfer_date):
    outgoing = Transaction.objects.create(
        user=transfer.user,
        card=from_card,
        category=None,
        amount=-amount,
        title=f"انتقال به {to_card.title}",
        description=description,
        transaction_date=transfer_date,
        transaction_kind=TransactionKind.TRANSFER,
        transfer=transfer,
    )
    incoming = Transaction.objects.create(
        user=transfer.user,
        card=to_card,
        category=None,
        amount=amount,
        title=f"انتقال از {from_card.title}",
        description=description,
        transaction_date=transfer_date,
        transaction_kind=TransactionKind.TRANSFER,
        transfer=transfer,
    )
    transfer.outgoing_transaction = outgoing
    transfer.incoming_transaction = incoming
    transfer.save(update_fields=["outgoing_transaction", "incoming_transaction"])


@transaction.atomic
def create_transfer(*, user, from_card, to_card, amount, description, transfer_date):
    if amount <= Decimal("0"):
        raise ValueError("مبلغ انتقال باید بزرگ‌تر از صفر باشد.")
    _validate_transfer_cards(from_card, to_card, user)
    _validate_sufficient_balance(from_card, amount)

    transfer = Transfer.objects.create(
        user=user,
        from_card=from_card,
        to_card=to_card,
        amount=amount,
        description=description,
        transfer_date=transfer_date,
    )
    _create_transfer_transactions(
        transfer,
        from_card=from_card,
        to_card=to_card,
        amount=amount,
        description=description,
        transfer_date=transfer_date,
    )
    return transfer


@transaction.atomic
def update_transfer(transfer, *, from_card, to_card, amount, description, transfer_date):
    if amount <= Decimal("0"):
        raise ValueError("مبلغ انتقال باید بزرگ‌تر از صفر باشد.")
    _validate_transfer_cards(from_card, to_card, transfer.user)

    outgoing = transfer.outgoing_transaction
    exclude = outgoing if outgoing and outgoing.card_id == from_card.pk else None
    _validate_sufficient_balance(from_card, amount, exclude_transaction=exclude)

    transfer.from_card = from_card
    transfer.to_card = to_card
    transfer.amount = amount
    transfer.description = description
    transfer.transfer_date = transfer_date
    transfer.save()

    outgoing = transfer.outgoing_transaction
    incoming = transfer.incoming_transaction

    if outgoing and incoming:
        outgoing.card = from_card
        outgoing.amount = -amount
        outgoing.title = f"انتقال به {to_card.title}"
        outgoing.description = description
        outgoing.transaction_date = transfer_date
        outgoing.save()

        incoming.card = to_card
        incoming.amount = amount
        incoming.title = f"انتقال از {from_card.title}"
        incoming.description = description
        incoming.transaction_date = transfer_date
        incoming.save()
    else:
        if outgoing:
            outgoing.delete()
        if incoming:
            incoming.delete()
        _create_transfer_transactions(
            transfer,
            from_card=from_card,
            to_card=to_card,
            amount=amount,
            description=description,
            transfer_date=transfer_date,
        )

    return transfer


@transaction.atomic
def delete_transfer(transfer):
    outgoing = transfer.outgoing_transaction
    incoming = transfer.incoming_transaction
    transfer.outgoing_transaction = None
    transfer.incoming_transaction = None
    transfer.save(update_fields=["outgoing_transaction", "incoming_transaction"])
    if outgoing:
        outgoing.delete()
    if incoming:
        incoming.delete()
    transfer.delete()
