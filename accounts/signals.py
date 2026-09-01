from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import User
from banking.services.setup import create_cash_card


@receiver(post_save, sender=User)
def setup_new_user(sender, instance, created, **kwargs):
    if created:
        create_cash_card(instance)
