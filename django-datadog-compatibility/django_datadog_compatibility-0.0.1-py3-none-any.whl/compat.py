"""Compatibility functions for DataDog integrations.
"""
from __future__ import absolute_import, print_function, unicode_literals

import logging
import six

from datadog import api, statsd
from requests.exceptions import HTTPError

from .utils import init_datadog

logger = logging.getLogger(__name__)


def create_event(title, fmt_text, priority='low', text_args=(),
                 alert_level='info', **kwargs):
    """Create a DataDog Event.

    :type title: str
    :param title: The event title for DataDog.

    :type fmt_text: str
    :param fmt_text: The pre-formatted text string. Send in the format string
    and text args for logging. This must be % formatted.

    :type aggregation_key: str
    :param aggregation_key: Aggregate results on DataDog

    :type priority: str
    :param priority: "low", "normal"

    :type text_args: tuple
    :param text_args: The tuple of text args for fmt_text

    :type alert_level: str
    :param alert_level: "error", "warning", "info", or "success"
    """
    if init_datadog():
        try:
            create_kwargs = {
                'title': title,
                'text': fmt_text % text_args,
                'priority': priority,
                'alert_level': alert_level,
            }
            create_kwargs.update(kwargs)
            api.Event.create(**create_kwargs)
        except HTTPError as exc:
            logger.error('Error occurred connecting to DataDog: %s',
                         six.text_type(exc))
            logger.log(alert_level, fmt_text, *text_args)
        except Exception as exc:
            logger.error('An unknown error occurred in event: %s',
                         six.text_type(exc))
    else:
        logger.log(loglevel(alert_level), fmt_text, *text_args)


def create_gauge(title, value, tags=None, sample_rate=1):
    """Create a statsd gauge event for DataDog.

    :type title: str
    :param title: The metric to track

    :type value: numeric
    :param value: The value of the metric

    :type tags: list
    :param tags: The tags to attach to the metric for analysis

    :type sample_rate: int
    :param sample_rate:
    """
    if init_datadog():
        try:
            statsd.gauge(metric=title, value=value, tags=tags,
                         sample_rate=sample_rate)
        except HTTPError as exc:
            logger.error('DataDog returned error calling statsd %s',
                         six.text_type(exc))
        except Exception as exc:
            logger.error('An unknown error occurred in gauge: %s',
                         six.text_type(exc))
    else:
        log_msg = '{}: %d'.format(title)
        logger.info(log_msg, value)


def loglevel(log_level):
    """Return the log-level for the logging module.

    :type log_level: str
    :param log_level: The log-level string

    :returns: int
    """
    levels = {
        'info': logging.INFO,
        'error': logging.ERROR,
        'warning': logging.WARNING,
        'success': logging.INFO,
    }
    return levels[log_level]
