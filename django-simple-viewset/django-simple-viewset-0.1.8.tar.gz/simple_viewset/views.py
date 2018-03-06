from django.conf.urls import url
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import get_permission_codename
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404


class ModelViewMixin(PermissionRequiredMixin):
    viewset = None
    detail_for = None

    def get_permission_required(self):
        opts = self.model._meta
        codename = get_permission_codename(self.action, opts)
        permission = '{0}.{1}'.format(opts.app_label, codename)

        return (permission,)

    def get_queryset(self):
        if self.queryset is not None:
            queryset = self.queryset
        elif self.viewset is not None and hasattr(self.viewset, 'get_queryset'):
            queryset = self.viewset.get_queryset(self.request)
        else:
            return self.model._default_manager.all()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if hasattr(self, 'list_display'):
            context.update({ 'list_display': self.list_display })

        if self.detail_for:
            if issubclass(self.__class__, (ModelListView, ModelCreateView)):
                parent_model = getattr(self.model, self.detail_for).field.related_model
                parent = get_object_or_404(self.get_parent_queryset(parent_model), pk=self.kwargs.get(self.detail_for))
            else:
                parent = getattr(self.object, self.detail_for)

            context.update({ 'parent': parent })

        return context

    def get_success_url(self):
        url = reverse_lazy('{0}_list'.format(self.model._meta.model_name))
        if self.detail_for:
            parent_pk = getattr(self.object, self.detail_for).pk
            url = reverse_lazy('{0}_list'.format(self.model._meta.model_name), args=(parent_pk,))

        return url

    def get_template_names(self):
        opts = self.model._meta
        return [
            '{}/{}_{}.html'.format(opts.app_label, opts.model_name, self.template_name_suffix),
            'simple_viewset/{}.html'.format(self.template_name_suffix),
        ]

    def get_parent_queryset(self, parent_model):
        if self.viewset is not None and hasattr(self.viewset, 'get_parent_queryset'):
            queryset = self.viewset.get_parent_queryset(parent_model)
        else:
            queryset = parent_model.objects.all()

        return queryset


class ModelListView(ModelViewMixin, ListView):
    action = 'read'
    list_display = None
    template_name_suffix = 'list'

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.detail_for:
            kwargs = {
                self.detail_for: self.kwargs.get(self.detail_for)
            }
            queryset = queryset.filter(**kwargs)

        return queryset


class ModelDetailView(ModelViewMixin, DetailView):
    action = 'read'
    template_name_suffix = 'detail'


class ModelCreateView(ModelViewMixin, CreateView):
    action = 'add'
    fields = '__all__'
    template_name_suffix = 'form'

    def get_initial(self):
        initial = None
        if self.detail_for:
            initial = {
                self.detail_for: self.kwargs.get(self.detail_for)
            }

        return initial


class ModelUpdateView(ModelViewMixin, UpdateView):
    action = 'change'
    fields = '__all__'
    template_name_suffix = 'form'


class ModelDeleteView(ModelViewMixin, DeleteView):
    action = 'delete'
    template_name_suffix = 'confirm_delete'


class ModelViewSet(object):
    model = None
    detail_for = None
    list_display = None
    list_view_class = ModelListView
    detail_view_class = ModelDetailView
    create_view_class = ModelCreateView
    update_view_class = ModelUpdateView
    delete_view_class = ModelDeleteView

    def urls(self):
        model_name = self.model._meta.model_name
        regexp = ''

        if self.detail_for:
            regexp = self.detail_for + '/(?P<{0}>[0-9]+)/'.format(self.detail_for)

        return [
            url(r'^{0}/{1}$'.format(model_name, regexp), self.get_view('list'), name='{0}_list'.format(model_name)),
            url(r'^{0}/(?P<pk>[0-9]+)/$'.format(model_name), self.get_view('detail'), name='{0}_detail'.format(model_name)),
            url(r'^{0}/add/{1}$'.format(model_name, regexp), self.get_view('create'), name='{0}_add'.format(model_name)),
            url(r'^{0}/(?P<pk>[0-9]+)/update/$'.format(model_name), self.get_view('update'), name='{0}_update'.format(model_name)),
            url(r'^{0}/(?P<pk>[0-9]+)/delete/$'.format(model_name), self.get_view('delete'), name='{0}_delete'.format(model_name)),
        ]

    def get_view(self, option):
        attr = '{0}_view_class'.format(option)
        kwargs = {
            'model': self.model,
            'viewset': self,
            'detail_for': self.detail_for,
        }

        if option == 'list':
            kwargs.update({ 'list_display': self.list_display })
            if self.list_display:
                kwargs.update({ 'template_name_suffix': 'table' })

        return getattr(self, attr, None).as_view(**kwargs)

    def get_parent_queryset(self, parent_model):
        return parent_model.objects.all()
