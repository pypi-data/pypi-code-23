from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from restify.models import ApiKey


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_api_key(sender, **kwargs):
    """
    A signal for hooking up automatic ``ApiKey`` creation.
    """
    if kwargs.get('created') is True:
        ApiKey.objects.create(user=kwargs.get('instance'))