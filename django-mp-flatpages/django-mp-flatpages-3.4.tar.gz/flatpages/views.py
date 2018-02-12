
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.views import redirect_to_login

from flatpages.models import FlatPage
from flatpages.settings import DEFAULT_TEMPLATE


def flatpage(request, url):

    if not url.startswith('/'):
        url = '/' + url

    obj = get_object_or_404(FlatPage, url=url)

    if obj.registration_required and not request.user.is_authenticated():
        return redirect_to_login(request.path)

    template_name = obj.template_name or DEFAULT_TEMPLATE

    return render(request, template_name, {'flatpage': obj})
