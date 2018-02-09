# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class AppView(LoginRequiredMixin, TemplateView):
    """Class that can be reused for projects using ReactJS front-ends

    Notes:
        - To override login URL, you can set `LOGIN_URL` in settings.py
        - To override template_name, you can use AppView.as_view(template_name='new') in urls.py
    """
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    template_name = 'index.html'
