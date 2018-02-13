from django.template import Library


register = Library()


@register.filter
def meta(model, option):
    return getattr(model._meta, option, None)


@register.filter
def fields(object):
    return [(field.name, field.value_to_string(object)) for field in object._meta.fields]


@register.filter
def url_name(model, option):
    return '{0}_{1}'.format(model._meta.model_name, option)
