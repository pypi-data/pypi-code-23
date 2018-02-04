from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

#from django.template.loaders.app_directories import app_template_dirs
from django.template.loaders.app_directories import get_app_template_dirs

import os


register = template.Library()


@register.filter(name='template', needs_autoescape=True)
def template(path, autoescape=True):

    template_dir_list = []
    for template_dir in get_app_template_dirs('templates'):

        if path in os.listdir(template_dir):
            filename = os.path.join(template_dir, path)

            with open(filename) as templ:
                return mark_safe(templ.read())

    raise Exception("Missing ")
