from __future__ import absolute_import

from celery import task

from django.utils import timezone
from datetime import timedelta

from simple_django_logger.models import (
    Log,
    EventLog,
    RequestLog,
)


@task(name='Purge old logs')
def purge_old_logs(delete_before_days=7):
    """
    Purges old logs from the database table
    """
    delete_before_date = timezone.now() - timedelta(days=delete_before_days)
    logs_deleted = Log.objects.filter(
        created_on__lte=delete_before_date).delete()
    return logs_deleted


@task(name='Purge old event logs')
def purge_old_event_logs(delete_before_days=7):
    """
    Purges old event logs from the database table
    """
    delete_before_date = timezone.now() - timedelta(days=delete_before_days)
    logs_deleted = EventLog.objects.filter(
        created_on__lte=delete_before_date).delete()
    return logs_deleted


@task(name='Purge old request logs')
def purge_old_request_logs(delete_before_days=7):
    """
    Purges old request logs from the database table
    """
    delete_before_date = timezone.now() - timedelta(days=delete_before_days)
    logs_deleted = RequestLog.objects.filter(
        created_on__lte=delete_before_date).delete()
    return logs_deleted
