from django.apps import AppConfig
from os.path import dirname, basename

app_name = basename(dirname(__file__))

class Config(AppConfig):
    name = app_name
    verbose_name = ''
