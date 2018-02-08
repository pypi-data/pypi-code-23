from datadog import initialize

from django.conf import settings


def init_datadog():
    """Initialise DataDog for stats gathering.

    :returns: bool
    """
    if settings.DATADOG['ENABLED']:
        initialize(statsd_host=settings.STATSD_HOST,
                   statsd_port=settings.STATSD_PORT,
                   api_key=settings.DATADOG['API_KEY'],
                   app_key=settings.DATADOG['APP_KEY'])
        return True

    return False
