from uuid import uuid4
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
import os
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.conf import settings
import json

from django.http import HttpResponseRedirect
from django.contrib.auth.views import login
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
import json
from django.http import HttpResponse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit,Field,Layout,ButtonHolder,Fieldset,HTML

from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.core.urlresolvers import reverse 
from django.views.generic import View
from django.views.generic import CreateView,ListView,UpdateView,DeleteView


from . import forms
from . import models

class Edit(UpdateView):
    model = models.get_site_model()
    form_class = forms.Site
    #template_name = 'news.html'
    
    def get_initial(self):
        initial = super(Edit, self).get_initial()
        if not self.object:
            initial['default_domain'] = True
        return initial

    def form_valid(self, form):
        models.invalidate_site_cache(self.request)
        return super(Edit, self).form_valid(form)
    
    def get_object(self, queryset=None):
        return self.request.page_site

    def get_success_url(self):
        if self.request.POST.get('submit') == 'Save':
            return reverse("site_edit") 
        return "/%s" % self.request.GET.get('next','')

