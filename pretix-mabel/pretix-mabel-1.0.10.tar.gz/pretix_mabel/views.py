from pretix.control.permissions import (
    event_permission_required, EventPermissionRequiredMixin
)
from django.shortcuts import redirect
from django.core.urlresolvers import resolve, reverse
from pretix.control.views.event import (
    EventSettingsFormView, EventSettingsViewMixin)
from pretix.control.forms.event import (
    InvoiceSettingsForm,
)
from pretix.base.models.event import Event
from django import forms
from django.utils.translation import ugettext_lazy as _
from pretix.base.forms import SettingsForm
from django.forms import formset_factory, ModelForm, modelformset_factory
from django.contrib import messages
from pretix.base.models.items import Item
from .models import TicketLimit
from django.views.generic import FormView


class MabelSettingsForm(SettingsForm):
    user_sheet_id = forms.CharField(
        label=_("User Sheet ID"),
        required=True,
        help_text=_(
            "Sheet ID for the Google Sheet containing usernames, passwords and user types. "
            "The ID is contained within the URL: https://docs.google.com/spreadsheets/d/##KEY##/edit")
    )
    google_sheets_API_key = forms.CharField(
        label=_("Google Sheets API Key"),
        required=True,
        help_text=_(
            "API Key for Google sheets")
    )
    ibis_proxy_url = forms.CharField(
        label=_("IBIS proxy URL"),
        required=True,
        help_text=_(
            "For example, http://emmamayball.com/ibis")
    )
    ibis_institution_id = forms.CharField(
        label=_("IBIS Institution ID"),
        required=True,
        help_text=_(
            "For Emmanuel College, this should be \"EMMUG\"")
    )


class TicketLimitForm(ModelForm):
    event = forms.HiddenInput()

    class Meta:
        model = TicketLimit
        exclude = []

TicketLimitFormSet = modelformset_factory(
    TicketLimit, exclude=[], can_delete=True)


class MySettingsView(EventSettingsViewMixin, EventSettingsFormView):
    model = TicketLimit
    form_class = MabelSettingsForm
    template_name = 'pretix_mabel/settings.html'
    permission = 'can_change_event_settings'

    def get_success_url(self) -> str:
        return reverse('plugins:pretix_mabel:settings', kwargs={
            'organizer': self.request.event.organizer.slug,
            'event': self.request.event.slug
        })

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["ticket_limit_forms"] = TicketLimitFormSet(
            queryset=TicketLimit.objects.filter(event=self.request.event)
        )
        return ctx

    def post(self, request, **kwargs):
        mabel_form = self.get_form()
        formset = TicketLimitFormSet(request.POST)
        if all([formset.is_valid(), mabel_form.is_valid()]):
            formset.save()
            mabel_form.save()
            messages.success(self.request, _('Your changes have been saved. Please note that it can '
                                             'take a short period of time until your changes become '
                                             'active.'))
            return redirect(self.get_success_url())
        else:
            messages.error(self.request, _(
                'We could not save your changes. See below for details.'))
            return self.get(request)

