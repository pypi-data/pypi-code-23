from django.template import Library


register = Library()


@register.filter
def meta(model, option):
    return getattr(model._meta, option, None)


@register.filter
def fields(object):
    fields = []
    for field in object._meta.fields:
        choice_display = 'get_{0}_display'.format(field.name)
        if hasattr(object, choice_display):
            value = getattr(object, choice_display)
        else:
            value = getattr(object, field.name)

        value = value or ''

        fields.append((field, value))

    return fields


@register.filter
def url_name(model, option):
    return '{0}_{1}'.format(model._meta.model_name, option)
