from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models


class A0User(AbstractBaseUser):
    """
    The user model. Relies on JSONField to store the full user profile.
    @uid: Auth0 user_id
    @name: User's name
    @email: User's email
    """
    uid = models.CharField(max_length=140, null=False, db_index=True, primary_key=True, unique=True)
    name = models.CharField(max_length=140, null=True, blank=True)
    email = models.EmailField(max_length=140, null=False, blank=False)
    email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'uid'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['uid', 'email']

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name
