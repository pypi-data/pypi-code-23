# coding: utf-8
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import (
    Enterprise,
    Project,
    Task
)


@receiver(pre_save, sender=Enterprise)
@receiver(pre_save, sender=Project)
@receiver(pre_save, sender=Task)
def calculate_900913_geometry(sender, instance, *args, **kwargs):
    """
    Calculates and sets the 900913 geometry if
    regular geometry is given
    """
    if instance.geometry:
        instance.geometry_900913 = instance.geometry.transform(900913, clone=True)
