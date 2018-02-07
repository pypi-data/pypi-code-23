# -*- coding: utf-8 -*-
"""EmailUser models"""

import random, string
from datetime import datetime, timedelta
import logging
import hashlib
import pytz

from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

logger = logging.getLogger(__name__)

class TokenException(Exception):
    """Token Empty exception"""
    def __init__(self, value):
        self.value = value
        logger.error(self.value)


def gen_hash(size):
    """Generate some hash with given size (length)"""
    alph = "%s%s" % (string.digits, string.ascii_letters)
    h = ''.join([random.choice(alph) for i in range(0, size)])
    return h

class UserOption(models.Model):
    """Table for keep user options"""

    user = models.ForeignKey('EmailUser', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=250)

    def __unicode__(self):
        return "(%s) %s:%s" % (self.user, self.name, self.value[:10])

class EmailUser(models.Model):
    """EmailUser model,
    we keep here tokens"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    added = models.DateTimeField(auto_now_add=True)
    last_auth = models.DateTimeField(auto_now=True)
    auth_token = models.CharField(max_length=150, default="", null=True,
                                  blank=True)
    token_generated = models.DateTimeField(null=True, blank=True)
    is_authenticated = models.BooleanField(default=False)

    auth_token_len = 20
    token_timelife = timedelta(days=1)

    def do_auth(self, token):
        """Check if token is valid"""
        try:
            token = str(token)
        except ValueError:
            raise TokenException("Token should contain only acsi characters")

        if len(token) < self.auth_token_len:
            raise TokenException(("Token length should be at"
                                  "least %s characters: %s (%s)")
                                 % (self.auth_token_len, token, len(token)))

        if len(self.auth_token) < self.auth_token_len:
            raise TokenException(("Token is invalid. Create new token with "
                                  "generate_token()"))

        if self.token_generated is None:
            raise TokenException(("token_generated is invalid. Create new "
                                  "token with generate_token()"))
        if settings.USE_TZ:
            tz = pytz.timezone(settings.TIME_ZONE)
            if datetime.now(tz) - self.token_generated > self.token_timelife:
                raise TokenException(("Token is outdated Create new token with "
                                      "generate_token()"))
        else:
            if datetime.now() - self.token_generated > self.token_timelife:
                raise TokenException(("Token is outdated Create new token with "
                                      "generate_token()"))


        authenticated = False
        if self.auth_token == token:
            authenticated = True
            #self.auth_token = ""
            self.is_authenticated = True
            self.last_auth = datetime.now()
            self.save()
        return authenticated

    def generate_token(self):
        """Create new token and store it in database"""
        from random import randint
        if settings.USE_TZ:
            tz = pytz.timezone(settings.TIME_ZONE)
            self.token_generated = datetime.now(tz)
        else:
            self.token_generated = datetime.now()

        date_str = self.token_generated.strftime('%m/%d/%Y')
        hash_string = "%s%s%s" % (self.pk, settings.SECRET_KEY, date_str)

        #self.auth_token = gen_hash(self.auth_token_len + randint(2, 20))
        self.auth_token = hashlib.sha256(hash_string.encode('utf8')).hexdigest()
        self.save()

        return self.auth_token

    def get_option(self, name):
        """Get user option"""
        try:
            uopt = UserOption.objects.get(user=self, name=name)
        except UserOption.DoesNotExist:
            return False
        return uopt.value

    def set_option(self, name, value):
        """Set user option"""
        UserOption.objects.get_or_create(user=self, name=name,
                                         value=value)
        return None

    def __unicode__(self):
        return self.user.email

class EmailUserForm(forms.Form):
    """EmailUser form (for login/registration"""
    email = forms.EmailField()

    def clean_email(self):
        """All emails should be lower case"""
        super(EmailUserForm, self).clean()
        data = self.cleaned_data['email'].lower()
        return data

@receiver(post_save, sender=User)
def create_email_user(sender, **kw):
    """Here we create emailuser each time new user added"""
    user = kw["instance"]
    if kw["created"]:
        euser = EmailUser(user=user)
        euser.save()

def manual_create_email_user(user):
    """Helper for creating meailuser manually"""
    euser = EmailUser(user=user)
    euser.save()
