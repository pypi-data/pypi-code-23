from django.conf.urls import url
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import get_permission_codename
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import PermissionRequiredMixin


class ModelViewMixin(PermissionRequiredMixin):
    viewset = None

    def get_permission_required(self):
        opts = self.model._meta
        codename = get_permission_codename(self.action, opts)
        permission = '{0}.{1}'.format(opts.app_label, codename)

        return (permission,)

    def get_queryset(self):
        if self.queryset is not None:
            queryset = self.queryset
        elif self.viewset is not None and hasattr(self.viewset, 'get_queryset'):
            queryset = self.viewset.get_queryset()
        else:
            return self.model._default_manager.all()

        return queryset


class ModelListView(ModelViewMixin, ListView):
    template_name = 'simple_viewset/list.html'
    action = 'read'


class ModelDetailView(ModelViewMixin, DetailView):
    template_name = 'simple_viewset/detail.html'
    action = 'read'


class ModelCreateView(ModelViewMixin, CreateView):
    template_name = 'simple_viewset/form.html'
    action = 'add'
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('{0}_list'.format(self.model._meta.model_name))


class ModelUpdateView(ModelViewMixin, UpdateView):
    template_name = 'simple_viewset/form.html'
    action = 'change'
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('{0}_list'.format(self.model._meta.model_name))


class ModelDeleteView(ModelViewMixin, DeleteView):
    template_name = 'simple_viewset/confirm_delete.html'
    action = 'delete'

    def get_success_url(self):
        return reverse_lazy('{0}_list'.format(self.model._meta.model_name))


class ModelViewSet(object):
    model = None
    list_view_class = ModelListView
    detail_view_class = ModelDetailView
    create_view_class = ModelCreateView
    update_view_class = ModelUpdateView
    delete_view_class = ModelDeleteView

    def urls(self):
        model_name = self.model._meta.model_name
        return [
            url(r'{0}/$'.format(model_name), self.get_view('list'), name='{0}_list'.format(model_name)),
            url(r'{0}/(?P<pk>[0-9]+)/$'.format(model_name), self.get_view('detail'), name='{0}_detail'.format(model_name)),
            url(r'{0}/add/$'.format(model_name), self.get_view('create'), name='{0}_add'.format(model_name)),
            url(r'{0}/(?P<pk>[0-9]+)/update/$'.format(model_name), self.get_view('update'), name='{0}_update'.format(model_name)),
            url(r'{0}/(?P<pk>[0-9]+)/delete/$'.format(model_name), self.get_view('delete'), name='{0}_delete'.format(model_name)),
        ]

    def get_view(self, option):
        attr = '{0}_view_class'.format(option)
        return getattr(self, attr, None).as_view(model=self.model, viewset=self)
