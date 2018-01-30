# coding: utf-8
from django.dispatch import Signal

pre_sync = Signal(providing_args=['fonte_externa'])
post_sync = Signal(providing_args=['fonte_externa', "sucesso"])
