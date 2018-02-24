from django.db import models
from django.contrib.auth.models import User

# Create your models here.

"""Extending the Django's User model"""


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)


class Organization(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    # when new user is created,
    # a implicit, default organization is also created with the same name
    default = models.BooleanField(default=False)
