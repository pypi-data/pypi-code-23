import json
import re
import os
import workon
from django.conf import settings
from django import template


register = template.Library()


@register.simple_tag
def settings_value(name):
    return getattr(settings, name, os.environ.get(name, ''))

@register.filter
def from_settings(name):
    return getattr(settings, name, os.environ.get(name, ''))

@register.filter(name='divide_by')
def divide_by(value, arg):
    try:
        return int(int(value) / int(arg))
    except (ValueError, ZeroDivisionError):
        return None

@register.filter(name='range')
def range_filter(x):
    return range(x)
    
@register.filter
def get(object, name, default=None):
    return object.get(name, default)

@register.filter(name="getattr")
def get_attr(object, name, default=None):
    return getattr(object, name, default)

@register.filter()
def currency(value):
    return workon.currency(value if value else 0)

@register.filter()
def pluralize(value):
    return "s" if value else ""

@register.filter()
def typeof(obj):
    return type(obj)

@register.filter
def startswith(str, compare):
    return str.startswith(compare)

@register.filter
def jsonify(obj):
    if obj is None:
        return "{}"
    if isinstance(obj,dict):
        return json.dumps(obj)
    elif isinstance(obj,list):
        return json.dumps(obj)
    elif type(obj) == type({}.keys()):
        return json.dumps(list(obj))
    else:
        obj = re.sub(r'([\w\d_]+)\:', '"\\1":', obj)
        obj = re.sub(r'\'', '"', obj)
        obj = re.sub(r'\/\/\s*[\w\s\d]+', '', obj)
        obj = re.sub(r'Date\.UTC\(.+\)', '""', obj)

        try:
            return json.dumps(json.loads(obj))
        except:
            return json.loads(json.dumps(obj))

@register.filter
def sanitize(html):
    workon.sanitize(html)


from workon.templatetags.workon_urls import lazy_register
lazy_register(register)


from workon.templatetags.workon_compress import lazy_register
lazy_register(register)


from workon.templatetags.workon_assets import lazy_register
lazy_register(register)


from workon.templatetags.workon_form import lazy_register
lazy_register(register)


from workon.templatetags.workon_metas import lazy_register
lazy_register(register)


from workon.templatetags.workon_thumbnail import lazy_register
lazy_register(register)