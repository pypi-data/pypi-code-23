from django.db import models

from django.contrib.redirects.models import Redirect


QUERY_PARAM_CHOICES = (
    ('REMOVE', 'Remove all requested query params from query'),
    ('REDIRECT_WINS', 'Overwrite query params with values in redirect'),
    ('QUERY_WINS', 'Overwrite redirect params with values in query')
)


class RedirectWithQueryParams(models.Model):

    redirect = models.OneToOneField(Redirect, on_delete=models.CASCADE)

    query_param_behavior = models.CharField(
        max_length=15,
        choices=QUERY_PARAM_CHOICES,
        default=QUERY_PARAM_CHOICES[0][0],
        verbose_name='Redirect with Query Parameters',
    )
