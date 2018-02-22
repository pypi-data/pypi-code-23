"""
Fake settings acquisition
"""


class Settings(object):
    amqp = {}


class DefaultSettings(Settings):
    amqp = {
        'URI': 'sqs://LOGIN:PASSWORD@',
        'TRANSPORT': {
            'region': 'eu-west-1',
            'queue_name_prefix': 'dev-%(hostname)s-'
        },
        'OFFICE_HOURS': False,
        'QUEUES': {}
    }


class DjangoSettings(DefaultSettings):

    def __init__(self):
        from django.conf import settings

        self.amqp.update(settings.SWARM_BUS)


# TODO: add more backends when needed
try:
    from swarm.config import settings
except ImportError:
    try:
        settings = DjangoSettings()
    except:
        settings = DefaultSettings()
