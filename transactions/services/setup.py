from transactions.models import CategoryType, TransactionCategory

DEFAULT_EXPENSE_CATEGORIES = [
    "کافه و رستوران",
    "رفت و آمد",
    "خرید لباس",
    "خرید روزمره",
    "قبض و خدمات",
    "درمان",
    "آموزش",
    "تفریح",
    "سفر",
    "کمک‌های خیریه",
    "هدیه",
    "سایر هزینه‌ها",
]

DEFAULT_INCOME_CATEGORIES = [
    "حقوق",
    "پروژه و فریلنس",
    "فروش",
    "سرمایه‌گذاری",
    "هدیه دریافتی",
    "سایر درآمدها",
]


def create_default_categories(user):
    for name in DEFAULT_EXPENSE_CATEGORIES:
        TransactionCategory.objects.get_or_create(
            user=user,
            name=name,
            category_type=CategoryType.EXPENSE,
        )
    for name in DEFAULT_INCOME_CATEGORIES:
        TransactionCategory.objects.get_or_create(
            user=user,
            name=name,
            category_type=CategoryType.INCOME,
        )
