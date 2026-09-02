from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import User
from banking.services.setup import create_cash_card
from transactions.services.setup import create_default_categories


@receiver(post_save, sender=User)
def setup_new_user(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            create_cash_card(instance)
            create_default_categories(instance)
