import hmac
import uuid

try:
    from hashlib import sha1
except ImportError:
    import sha
    sha1 = sha.sha

from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class ApiKey(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, models.CASCADE, related_name='api_key')
    key = models.CharField(max_length=128, blank=True, default='', db_index=True)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u"%s for %s" % (self.key, self.user)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()

        return super(ApiKey, self).save(*args, **kwargs)

    def generate_key(self):
        # Get a random UUID.
        new_uuid = uuid.uuid4()
        # Hmac that beast.
        return hmac.new(new_uuid.bytes, digestmod=sha1).hexdigest()
