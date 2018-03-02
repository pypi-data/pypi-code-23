from django.db.models import Max, Min


def field_list_filter(model, **kwargs):
    response = {**kwargs}
    lookup_field = response['lookup_field']
    response['values'] = model.objects.values(lookup_field).distinct(lookup_field)
    return response


def related_field_list_filter(model, **kwargs):
    related_model = kwargs.pop('related_model')
    response = {**kwargs}
    response['values'] = related_model['cls'].objects.values(*related_model['fields'])
    if related_model.get('distinct_fields'):
        response['values'] = response['values'].distinct(*related_model['distinct_fields'])
    return response


def bool_filter(model, **kwargs):
    response = {**kwargs}
    return response


def range_filter(model, **kwargs):
    response = {**kwargs}
    lookup_field = response['lookup_field']
    response['values'] = model.objects.aggregate(min_val=Min(lookup_field), max_val=Max(lookup_field))
    return response


def related_range_filter(model, **kwargs):
    related_model = kwargs.pop('related_model')
    lookup_field = kwargs['lookup_field']['field']
    response = {**kwargs}
    response['values'] = related_model['cls'].objects.aggregate(min_val=Min(lookup_field), max_val=Max(lookup_field))
    return response
