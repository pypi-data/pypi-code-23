from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from .models import APIUser
import django.dispatch
import logging

logger = logging.getLogger(__name__)


#####-----< Triggers >----#####
# fired when a form is submitted to the backend, but before the submission is cleaned / validated
form_submitted = django.dispatch.Signal(providing_args=["raw_data", "form_id"])

# fired after a form submission is cleaned / validated
form_submission_cleaned = django.dispatch.Signal(providing_args=["cleaned_data", "form_id", "submission_id"])

# fired on a form submission error
form_submission_error = django.dispatch.Signal(providing_args=["error", "raw_data", "form_id"])


#####-----< Listeners >----#####
@receiver(post_save, sender=APIUser)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        logger.debug('creating auth token for new API user')
        Token.objects.create(user=instance.auth_user)