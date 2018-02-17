from uuid import uuid4
import json

from django.core.files import File
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.views.generic import View
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.core.cache import cache
from django.views.generic.edit import FormMixin
from django.core.files.uploadedfile import UploadedFile
from . import forms
from . import models


class List(ListView):
    model = models.get_page_model()
    context_object_name = "page_list"  # needed for plugins
    template_name = 'page/page_list.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(List, self).dispatch(request, *args, **kwargs)


class Page_Form_Base(FormMixin):
    def get_form_kwargs(self):
        kwargs = super(Page_Form_Base, self).get_form_kwargs()
        kwargs['site'] = self.request.page_site
        return kwargs

    def get_success_url(self):
        if self.request.POST.get('submit') == 'Save':
            return reverse("page_edit", args=(self.object.slug,))
        else:
            return "/%s" % self.object.slug

    def get_context_data(self, **kwargs):
        context = super(Page_Form_Base, self).get_context_data(**kwargs)
        context['uuid'] = uuid4()
        context['PAGE_TINYMCE_PLUGINS'] = getattr(settings, 'PAGE_TINYMCE_PLUGINS', "")
        context['PAGE_TINYMCE_BUTTONS'] = getattr(settings, 'PAGE_TINYMCE_BUTTONS', "")
        return context

    def get_form_class(self):
        if self.request.user.has_perm('page.change_show_in_menu'):
            return forms.Page_Show_In_Menu
        else:
            return forms.Page

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.site = self.request.page_site
        if not self.object.pk:
            page_editor = models.Page_Editor(editor=self.request.page_user)
        else:
            page_editor = None

        self.object.save()
        form.save_m2m()

        if page_editor:
            page_editor.page = self.object
            page_editor.save()

        # save files
        for attachment in self.request.FILES.getlist('file'):
            if attachment:
                report_attachment = models.File(page=self.object, file=attachment)
                report_attachment.save()

                # save html5
        for attachment in models.UUID_File.objects.filter(uuid=self.request.POST.get('uuid')):
            if not str(attachment.pk) in self.request.POST.getlist('remove_new_file'):
                page_file = models.File(page=self.object, file=attachment.file)
                page_file.save()
                attachment.delete()

        if len(self.request.FILES.getlist('file')):
            self.object.save()

            # remove files
        for file_pk in self.request.POST.getlist('remove_file'):
            try:
                file_remove = models.File.objects.get(pk=file_pk, )
                file_remove.delete()
            except models.File.DoesNotExist:
                pass

        cache.delete(models.get_page_key(self.request.page_site.pk, self.object.slug))
        return HttpResponseRedirect(self.get_success_url())


class Add(Page_Form_Base, CreateView):
    model = models.get_page_model()
    form_class = forms.Page
    template_name = 'page/page_form.html'

    def get_initial(self):
        initial = super(Add, self).get_initial()
        initial['slug'] = self.request.GET.get('slug', '').rstrip('/')
        if initial['slug'] == "":
            initial['slug'] = "default"

        initial['title'] = initial['slug']

        return initial

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm(models.get_class_model_perm(models.PAGE_PAGE, 'add')):
            return HttpResponse('Sorry, You do not have access!')
        return super(Add, self).dispatch(request, *args, **kwargs)


class Edit(Page_Form_Base, UpdateView):
    model = models.get_page_model()
    template_name = 'page/page_form.html'

    def get_object(self, queryset=None):
        try:
            page = models.get_page_model().objects.get(site=self.request.page_site, slug=self.kwargs['slug'])
        except:
            page = None
        return page

    def get_context_data(self, **kwargs):
        kwargs = super(Edit, self).get_context_data(**kwargs)
        kwargs['editors'] = models.Page_Editor.objects.filter(page=self.object)
        kwargs['files'] = models.File.objects.filter(page=self.object)
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object:
            return HttpResponseNotFound('Page not found')

        if not self.request.user.has_perm(models.get_class_model_perm(models.PAGE_PAGE, 'change')):
            if models.Page_Editor.objects.filter(editor=request.page_user, page=self.object).count() < 1:
                return HttpResponse('Sorry, You do not have access!')

        return super(Edit, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.request.user.has_perm(models.get_class_model_perm(models.PAGE_PAGE, 'change')):
            if models.Page_Editor.objects.filter(editor=request.page_user, page=self.object).count() < 1:
                return HttpResponse('Sorry, You do not have access!')

        return super(Edit, self).post(request, *args, **kwargs)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(Edit, self).dispatch(request, *args, **kwargs)


class Delete(DeleteView):
    model = models.get_page_model()
    template_name = 'page/page_confirm_delete.html'

    def get_success_url(self):
        cache.delete(models.get_page_key(self.request.page_site.pk, self.object.slug))
        return reverse("page_list")

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm(models.get_class_model_perm(models.PAGE_PAGE, 'delete')):
            return HttpResponse('Sorry, You do not have rights!')

        return super(Delete, self).dispatch(request, *args, **kwargs)


class Edit_Links(View):
    def get(self, request, *args, **kwargs):
        response = "["
        wrote_first = False

        response += "{\"title\": \"Files\", \"menu\": ["

        uuid = self.request.GET.get('uuid')
        if uuid:
            for attachment in models.UUID_File.objects.filter(uuid=uuid):
                if (wrote_first):
                    response += ","
                else:
                    wrote_first = True
                response += "{\"title\": \"%s\", value: \"%s\"}" % (attachment.filename(), attachment.file.url)

        if 'slug' in self.kwargs:
            page = models.get_page_model().objects.get(site=self.request.page_site, slug=self.kwargs['slug'])
            if page:
                for file in page.page_file.all():
                    if (wrote_first):
                        response += ","
                    else:
                        wrote_first = True
                    response += "{\"title\": \"%s\", \"value\": \"%s\"}" % (file.filename(), file.file.url)
        response += "]},"
        wrote_first = False

        response += "{\"title\": \"Pages\", \"menu\": ["

        # get all pages
        pages = models.get_page_model().objects.all().filter(site=self.request.page_site).order_by('slug')
        for page_entry in pages:
            if (wrote_first):
                response += ","
            else:
                wrote_first = True
            response += "{\"title\": \"%s\", \"value\": \"%s\"}" % (page_entry.slug, page_entry.slug)
        response += "]}"

        response += "]"
        return HttpResponse(response)


class Edit_Images(View):
    def get(self, request, *args, **kwargs):
        response = "["
        wrote_first = False

        uuid = self.request.GET.get('uuid')
        if uuid:
            for attachment in models.UUID_File.objects.filter(uuid=uuid):
                if (wrote_first):
                    response += ","
                else:
                    wrote_first = True
                response += "{title: '%s', value: '%s'}" % (attachment.filename(), attachment.file.url)

        if 'slug' in self.kwargs:
            page = models.get_page_model().objects.get(site=self.request.page_site, slug=self.kwargs['slug'])
            if page:
                for file in page.page_file.all():
                    if file.filename().lower().endswith(('jpg', 'jpeg', 'gif', 'tiff', 'png')):
                        if (wrote_first):
                            response += ","
                        else:
                            wrote_first = True
                        response += "{title: '%s', value: '%s'}" % (file.filename(), file.file.url)

        response += "]"
        return HttpResponse(response)


class Upload_File(View):
    # sizeLimit = 1024000

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('page.add_file'):
            return HttpResponse('Sorry, You do not have rights!')

        return super(Upload_File, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        files = []

        f = request.FILES['files[]']
        wrapped_f = UploadedFile(f)
        filename = wrapped_f.name
#        filesize = wrapped_f.file.size

        uuidfile = models.UUID_File(
            file=File(f, filename),
            uuid=self.request.POST['uuid']
        )
        uuidfile.save()

        files.append({
            "name": filename,
            "url": uuidfile.file.url,
            "pk": uuidfile.pk
        })

        response = {
            'files': files
        }
        return HttpResponse(json.dumps(response))
