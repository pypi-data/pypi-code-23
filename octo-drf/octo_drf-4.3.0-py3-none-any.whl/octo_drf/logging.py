
import requests

from django.conf import settings
from django.utils.log import AdminEmailHandler

from octo_drf.settings import project_settings
DEBUG = settings.DEBUG
PROJECT_NAME = settings.PROJECT_NAME.upper()
SUBS = project_settings['logging']['subs']

# Old slack handlers

def exclude_localhost(record):
    log_message = True
    host = record.request.META['HTTP_HOST']
    local_hosts = ['127', '0', 'local']
    for i in local_hosts:
        if host.startswith(i):
            log_message = False
    return log_message


class SlackHandler(AdminEmailHandler):

    def parse_log(self, message):
        request_info = message[:message.find('Django Version')]
        traceback = message[message.find('Traceback'):message.find('COOKIES')]
        subs = ''.join(['<@{}>'.format(name) for name in SUBS])
        message = '{subs}\n*{project}*\n\n\n*REQUEST INFO*\n{request_info}\n*TRACEBACK*\n{traceback}'
        return message.format(
            subs=subs,
            project=PROJECT_NAME,
            request_info=request_info,
            traceback=traceback
        )

    def send_mail(self, subject, message, *args, **kwargs):
        log = self.parse_log(message)
        if DEBUG:
            url = 'https://hooks.slack.com/services/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'
        else:
            url = 'https://hooks.slack.com/services/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'
        requests.post(
            url,
            json={'text': log,
                  "username": "error-bot",
                  "icon_emoji": ":bike:"}
        )


# old slack logging

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'filters': {
#         'require_debug_false': {
#             '()': 'django.utils.log.RequireDebugFalse',
#         },
#         'require_debug_true': {
#             '()': 'django.utils.log.RequireDebugTrue',
#         },
#         'exclude_localhost': {
#             '()': 'django.utils.log.CallbackFilter',
#             'callback': exclude_localhost,
#         },
#     },
#     'handlers': {
#         'slack_dev': {
#             'class': 'octo_drf.logging.SlackHandler',
#             'level': 'ERROR',
#             'filters': ['require_debug_true', 'exclude_localhost'],
#         },
#         'slack_prod': {
#             'class': 'octo_drf.logging.SlackHandler',
#             'level': 'ERROR',
#             'filters': ['require_debug_false', 'exclude_localhost'],
#         },
#     },
#     'loggers': {
#         'django.request': {
#             'handlers': ['slack_dev', 'slack_prod'],
#             'level': 'ERROR',
#             'propagate': True,
#         },
#     },
# }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'opbeat': {
            'level': 'WARNING',
            'class': 'opbeat.contrib.django.handlers.OpbeatHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'site': {
            'level': 'WARNING',
            'handlers': ['opbeat'],
            'propagate': False,
        },
        'opbeat.errors': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'console_warnings': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False
        }
    },
}
