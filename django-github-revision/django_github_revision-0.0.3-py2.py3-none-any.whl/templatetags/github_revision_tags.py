from django import template
from django.utils.safestring import mark_safe

from github_revision import context_processors
from django.utils.html import conditional_escape as esc

register = template.Library()


@register.simple_tag
def github_link():
    github = context_processors.github_revision()['github']
    revision_id = github['revision_id'][:7]
    result = '<a href="{link}">{revision_id}</a>'.format(link=esc(github['url']), revision_id=esc(revision_id))
    return mark_safe(result)