from datetime import date

from django import forms
from django.core.exceptions import ValidationError

from core.dates import gregorian_to_jalali, jalali_to_gregorian


class JalaliDateField(forms.DateField):
    widget = forms.TextInput(
        attrs={
            "class": "jalali-date-input",
            "placeholder": "۱۴۰۵/۰۶/۱۰",
            "autocomplete": "off",
        }
    )

    def prepare_value(self, value):
        if isinstance(value, date):
            return gregorian_to_jalali(value)
        return value

    def to_python(self, value):
        if not value:
            return None
        if isinstance(value, date):
            return value
        try:
            return jalali_to_gregorian(str(value))
        except (ValueError, TypeError) as exc:
            raise ValidationError(str(exc)) from exc
