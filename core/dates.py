from datetime import date, datetime, timedelta

import jdatetime


JALALI_DISPLAY_FORMAT = "%Y/%m/%d"


def gregorian_to_jalali(value: date | datetime | None) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        value = value.date()
    jalali = jdatetime.date.fromgregorian(date=value)
    return jalali.strftime(JALALI_DISPLAY_FORMAT)


def jalali_to_gregorian(value: str) -> date:
    value = value.strip().replace("-", "/")
    parts = value.split("/")
    if len(parts) != 3:
        raise ValueError("فرمت تاریخ نامعتبر است. از فرمت ۱۴۰۵/۰۶/۱۰ استفاده کنید.")
    year, month, day = (int(p) for p in parts)
    jalali = jdatetime.date(year, month, day)
    return jalali.togregorian()


def get_jalali_month_range(year: int, month: int) -> tuple[date, date]:
    start_j = jdatetime.date(year, month, 1)
    if month == 12:
        next_j = jdatetime.date(year + 1, 1, 1)
    else:
        next_j = jdatetime.date(year, month + 1, 1)
    end_j = next_j - jdatetime.timedelta(days=1)
    return start_j.togregorian(), end_j.togregorian()


def get_jalali_week_range(year: int, week: int) -> tuple[date, date]:
    year_start = jdatetime.date(year, 1, 1)
    greg_year_start = year_start.togregorian()
    days_until_saturday = (5 - greg_year_start.weekday()) % 7
    first_saturday = greg_year_start + timedelta(days=days_until_saturday)
    week_start = first_saturday + timedelta(weeks=week - 1)
    week_end = week_start + timedelta(days=6)
    return week_start, week_end


def current_jalali_date() -> jdatetime.date:
    return jdatetime.date.today()


def current_jalali_month() -> tuple[int, int]:
    today = jdatetime.date.today()
    return today.year, today.month


def current_jalali_week() -> tuple[int, int]:
    today = jdatetime.date.today()
    year = today.year
    year_start = jdatetime.date(year, 1, 1)
    greg_year_start = year_start.togregorian()
    days_until_saturday = (5 - greg_year_start.weekday()) % 7
    first_saturday = greg_year_start + timedelta(days=days_until_saturday)
    today_greg = today.togregorian()
    if today_greg < first_saturday:
        year -= 1
        year_start = jdatetime.date(year, 1, 1)
        greg_year_start = year_start.togregorian()
        days_until_saturday = (5 - greg_year_start.weekday()) % 7
        first_saturday = greg_year_start + timedelta(days=days_until_saturday)
    week = ((today_greg - first_saturday).days // 7) + 1
    return year, week


JALALI_MONTH_NAMES = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند",
]


def jalali_month_name(month: int) -> str:
    return JALALI_MONTH_NAMES[month - 1]


def jalali_month_choices() -> list[tuple[int, str]]:
    return [(index, name) for index, name in enumerate(JALALI_MONTH_NAMES, start=1)]


def jalali_week_for_gregorian(value: date) -> tuple[int, int]:
    jalali = jdatetime.date.fromgregorian(date=value)
    year = jalali.year
    year_start = jdatetime.date(year, 1, 1)
    greg_year_start = year_start.togregorian()
    days_until_saturday = (5 - greg_year_start.weekday()) % 7
    first_saturday = greg_year_start + timedelta(days=days_until_saturday)
    if value < first_saturday:
        year -= 1
        year_start = jdatetime.date(year, 1, 1)
        greg_year_start = year_start.togregorian()
        days_until_saturday = (5 - greg_year_start.weekday()) % 7
        first_saturday = greg_year_start + timedelta(days=days_until_saturday)
    week = ((value - first_saturday).days // 7) + 1
    return year, week
