from django import template
from django.middleware.csrf import get_token
from django.contrib.sites.shortcuts import get_current_site

register = template.Library()


@register.simple_tag(takes_context=True)
def get_site_address(context):
    """
    Используется в шаблонах для писем,
    request кладется в контекст руками, в сериалайзере или вью
    """
    return get_current_site(context['request'])
