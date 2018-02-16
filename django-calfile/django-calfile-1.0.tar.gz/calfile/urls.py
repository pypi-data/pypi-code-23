from django.urls import path
from .views import calfile

urlpatterns = [
    path('calfile/', calfile, name="calfile"),
]
