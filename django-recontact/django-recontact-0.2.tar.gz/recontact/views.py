from django.shortcuts import render
from django.core.mail import EmailMessage
from django.views.generic.base import View, TemplateView
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import RecontactForm

recontact_attrs = {
    'template_name': 'recontact/contact.html',
    'confirmation_template_name': 'recontact/message_sent.html',
    'addresses': ['postmaster@localhost'],
    'extra_context': {},
    'query': 'Recontact query:',
    'site_key': '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
}

try:
    from django.conf import settings
    recontact_attrs.update(settings.RECONTACT_CONFIG)
except:
    pass

class RecontactView(View):
    """
    A class based view which sends a contact email message and then
    redirects to an acknowledgement page.
    """
    template_name = recontact_attrs['template_name']
    confirmation_template_name = recontact_attrs['confirmation_template_name']
    addresses = recontact_attrs['addresses']
    extra_context = recontact_attrs['extra_context']
    query = recontact_attrs['query']
    site_key = recontact_attrs['site_key']
    
    def post(self, request, *args, **kwargs):
        form = RecontactForm(data=request.POST)
        context= self._get_extra_context(request, *args, **kwargs)
        if form.is_valid():
            subject = request.POST.get('subject', 'spam')
            sender = request.POST.get('sender', 'unknown')
            reply_to = request.POST.get('reply_to', '<>')
            message = request.POST.get('message', '')
            body = 'Message received from %s:\n\n%s'%(sender, message)
            email = EmailMessage(
                subject='%s %s'%(self.query, subject),
                to=self._get_addresses(request, *args, **kwargs),
                body=body,
                headers = {'Reply-To': reply_to}
            )
            email.send()
            return HttpResponseRedirect(request.META['HTTP_REFERER'] + 'sent/')
        context.update({'form': form, 'site_key': self.site_key})
        return render(request, self.template_name, context)

    def get(self, request, *args, **kwargs):
        context = self._get_extra_context(request, *args, **kwargs)
        if kwargs.get('sent', None):
            return render(request, self.confirmation_template_name, context)
        else:
            context.update({'form': RecontactForm(), 'site_key': self.site_key})
            return render(request, self.template_name, context)

    def _get_addresses(self, request, *args, **kwargs):
        if callable(self.addresses):
            return self.addresses(request, *args, **kwargs)
        else:
            return self.addresses

    def _get_extra_context(self, request, *args, **kwargs):
        if callable(self.extra_context):
            return self.extra_context(request, *args, **kwargs)
        else:
            return self.extra_context
