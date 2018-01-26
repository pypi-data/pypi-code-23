from enum import Enum
import json
from datetime import datetime, timedelta
from django.utils.translation import pgettext_lazy, ugettext as _
from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import Q
import raven_auth
from django import forms

from pretix.base.models.orders import Order
from pretix.presale.views import CartMixin
from pretix.presale.checkoutflow import TemplateFlowStep


class MySettingsView(EventSettingsViewMixin, EventSettingsFormView):
    model = Event
    permission = 'can_change_settings'
    form_class = MySettingsForm
    template_name = 'pretix_mabel/settings.html'

    def get_success_url(self, **kwargs):
        return reverse('plugins:myplugin:settings', kwargs={
            'organizer': self.request.event.organizer.slug,
            'event': self.request.event.slug,
        })
