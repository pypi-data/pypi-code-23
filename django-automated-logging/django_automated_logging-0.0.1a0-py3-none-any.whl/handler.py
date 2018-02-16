""" file containing the required handlers for cbrs global_logging - main part"""
from logging import Handler


class DatabaseHandler(Handler):
    """Handler for logging into any database"""
    def __init__(self):
        super(DatabaseHandler, self).__init__()

    def emit(self, record):
        # add to database
        # try - except -> preventing circular import
        # http://stackoverflow.com/questions/4379042/django-circular-model-import-issue

        try:
            if hasattr(record, 'mode'):
                if record.mode == 'model':
                    from .models import GlobalModelEventEntry

                    model_entry = GlobalModelEventEntry()

                    model_entry.application = record.data['instance']._meta.app_label
                    model_entry.message = record.message

                    if record.data['status'] == 'created':
                        status = 0
                    elif record.data['status'] == 'modified':
                        status = 1
                    elif record.data['status'] == 'purged':
                        status = 2
                    else:
                        status = 3

                    model_entry.mode = status
                    model_entry.object_name = record.data['instance']

                    import datetime
                    from .models import GlobalModelEntryChange

                    if record.data['status'] == 'modified':
                        try:
                            object_time = datetime.datetime.now() - datetime.timedelta(seconds=2)
                            changes = GlobalModelEntryChange.objects.filter(date_created__gte=object_time).\
                                filter(object_model=record.data['instance'].__class__.__name__).\
                                filter(object_id=record.data['instance'].pk).order_by('-date_created')

                            model_entry.modified_fields = changes[0]
                        except:
                            pass

                    model_entry.object_id = record.data['instance'].pk
                    model_entry.object_model = record.data['instance'].__class__.__name__

                    model_entry.user = record.data['user']

                    model_entry.save()
                elif record.mode == 'request':
                    from .models import GlobalRequestEventEntry

                    model_entry = GlobalRequestEventEntry()

                    model_entry.application = record.data['application']
                    model_entry.request = record.data['request_uri']
                    if record.data['user'] is not None:
                        model_entry.user = record.data['user']

                    model_entry.save()
            else:
                from .models import GlobalLoggingEntry

                model_entry = GlobalLoggingEntry()
                if hasattr(record, 'message'):
                    model_entry.message = record.message
                model_entry.level = record.levelno
                model_entry.path = record.pathname
                model_entry.line = record.lineno

                model_entry.save()
        except:
            pass
