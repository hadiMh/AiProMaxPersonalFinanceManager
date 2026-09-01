import re

from django.core.exceptions import ValidationError


def validate_card_number(value: str) -> None:
    if not value:
        return
    cleaned = value.replace(" ", "").replace("-", "")
    if not re.fullmatch(r"\d+", cleaned):
        raise ValidationError("شماره کارت فقط باید شامل اعداد باشد.")
    if len(cleaned) != 16:
        raise ValidationError("شماره کارت باید ۱۶ رقم باشد.")


def mask_card_number(value: str | None) -> str:
    if not value:
        return "—"
    cleaned = value.replace(" ", "").replace("-", "")
    if len(cleaned) < 8:
        return cleaned
    return f"{cleaned[:4]} **** **** {cleaned[-4:]}"
