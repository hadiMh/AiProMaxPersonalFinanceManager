from decimal import Decimal

from django import template

from core.dates import gregorian_to_jalali, jalali_month_name
from core.validators import mask_card_number

register = template.Library()


@register.filter
def jalali(value):
    return gregorian_to_jalali(value)


@register.filter
def mask_card(value):
    return mask_card_number(value)


@register.filter
def jalali_month(value):
    return jalali_month_name(int(value))


@register.filter
def money(value):
    if value is None:
        return "0"
    try:
        num = int(Decimal(str(value)))
    except (ValueError, TypeError, ArithmeticError):
        return value
    sign = "-" if num < 0 else ""
    return sign + f"{abs(num):,}"
