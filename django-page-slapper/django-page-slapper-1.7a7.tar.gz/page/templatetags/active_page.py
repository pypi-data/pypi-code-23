from django import template
from django.core.urlresolvers import reverse 

from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def active_page(page,request):
    """Returns True if active page
    """
    if request.path == '/' and page.slug == 'default':
        return True
    elif request.path == ('/' + page.slug):
        return True
    elif request.path == reverse("page_edit",args=[page.slug]): 
        return True
    
    return False

