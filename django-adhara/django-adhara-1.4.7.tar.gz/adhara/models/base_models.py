from django.db import models
from adhara.session import Session
from ..utilities import get_config
from ..exceptions import InvalidDatabaseSelected
from ..utilities import is_reference_field


def fill_ref_models(self, request=None, **kwargs):
    if request is None:
        return kwargs
    for field in self._meta.fields:
        vn = field.name
        if vn in kwargs:
            if kwargs[vn] == "0":
                del kwargs[vn]
            elif is_reference_field(field):
                db = Session.get_db(request)
                if type(kwargs[vn]) == str or type(kwargs[vn]) == int:
                    objects = field.related_model.objects
                    if db is None:
                        kwargs[vn] = objects.get(pk=kwargs[vn])
                    else:
                        kwargs[vn] = objects.using(db).get(pk=kwargs[vn])
                elif type(kwargs[vn]) == dict:
                    args = kwargs[vn]
                    args['request'] = request
                    kwargs[vn] = field.related_model(**args)
                    if db is None:
                        kwargs[vn].save()
                    else:
                        kwargs[vn].save(using=db)
    return kwargs


class AdharaManager(models.Manager):

    def __init__(self, *args, **kwargs):
        super(AdharaManager, self).__init__(*args, **kwargs)


class AdharaModel(models.Model):

    objects = AdharaManager()

    def fill_defaults(self, request, **kwargs):
        return kwargs

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            request = kwargs['request']
            del kwargs['request']
            kwargs = fill_ref_models(self, request, **kwargs)
            kwargs = self.fill_defaults(request, **kwargs)
        elif get_config("MULTI_TENANCY"):
            raise InvalidDatabaseSelected("multi tenancy enabled."
                                          " Please provide the request object to handle automatically")
        super(AdharaModel, self).__init__(*args, **kwargs)

    class Meta:
        abstract = True

    class Adhara:
        skip_serialization = False
        partial_fields = []
