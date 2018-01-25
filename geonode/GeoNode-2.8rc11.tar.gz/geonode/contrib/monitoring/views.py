# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2017 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

import json
import pytz
from datetime import datetime, timedelta
from django.shortcuts import render
from django import forms
from django.conf import settings
from django.views.generic.base import View
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt

from geonode.utils import json_response
from geonode.contrib.monitoring.collector import CollectorAPI
from geonode.contrib.monitoring.models import (
    Service,
    Host,
    Metric,
    ServiceTypeMetric,
    MetricLabel,
    MonitoredResource,
    ExceptionEvent,
    OWSService,
    NotificationCheck,
    MetricNotificationCheck,
)
from geonode.contrib.monitoring.models import do_autoconfigure
from geonode.contrib.monitoring.utils import TypeChecks, dump
from geonode.contrib.monitoring.service_handlers import exposes

# Create your views here.

capi = CollectorAPI()


class MetricsList(View):

    def get(self, *args, **kwargs):
        _metrics = capi.get_metric_names()
        out = []
        for srv, mlist in _metrics:
            out.append({'service': srv.name,
                        'metrics': [{'name': m.name, 'unit': m.unit, 'type': m.type}
                                    for m in mlist]})
        return json_response({'metrics': out})


class ServicesList(View):

    def get_queryset(self):
        return Service.objects.filter(active=True).select_related()

    def get(self, *args, **kwargs):
        q = self.get_queryset()
        out = []
        for item in q:
            out.append({'name': item.name,
                        'host': item.host.name,
                        'id': item.id,
                        'type': item.service_type.name,
                        'check_interval': item.check_interval.total_seconds(),
                        'last_check': item.last_check})

        return json_response({'services': out})


class HostsList(View):

    def get_queryset(self):
        return Host.objects.filter(active=True).select_related()

    def get(self, *args, **kwargs):
        q = self.get_queryset()
        out = []
        for item in q:
            out.append({'name': item.name, 'ip': item.ip})

        return json_response({'hosts': out})


class _ValidFromToLastForm(forms.Form):
    valid_from = forms.DateTimeField(required=False)
    valid_to = forms.DateTimeField(required=False)
    interval = forms.IntegerField(min_value=60, required=False)
    last = forms.IntegerField(min_value=60, required=False)

    def _check_timestamps(self):
        last = self.cleaned_data.get('last')
        vf = self.cleaned_data.get('valid_from')
        vt = self.cleaned_data.get('valid_to')
        if last and (vf or vt):
            raise forms.ValidationError('Cannot use last and valid_from/valid_to at the same time')

    def clean(self):
        super(_ValidFromToLastForm, self).clean()
        self._check_timestamps()


class CheckTypeForm(_ValidFromToLastForm):
    """
    Special form class to validate values from specific db dictionaries
    (services, resources, ows services etc)
    """
    def _check_type(self, tname):
        """
        Returns tname-specific object instance from db.

        Internally it uses geonode.contrib.monotoring.utils.TypeChecks
        to resolve field's value to object.

        """
        d = self.cleaned_data
        if not d:
            return
        val = d[tname]
        if not val:
            return
        tcheck = getattr(TypeChecks, '{}_type'.format(tname), None)
        if not tcheck:
            raise forms.ValidationError("No type check for {}".format(tname))
        try:
            return tcheck(val)
        except (Exception,), err:
            raise forms.ValidationError(err)


class MetricsFilters(CheckTypeForm):
    GROUP_BY_RESOURCE = 'resource'
    GROUP_BY_CHOICES = ((GROUP_BY_RESOURCE, "By resource",),)
    service = forms.CharField(required=False)
    label = forms.CharField(required=False)
    resource = forms.CharField(required=False)
    resource_type = forms.ChoiceField(choices=MonitoredResource.TYPES, required=False)
    ows_service = forms.CharField(required=False)
    service_type = forms.CharField(required=False)
    group_by = forms.ChoiceField(choices=GROUP_BY_CHOICES, required=False)

    def clean_resource(self):
        return self._check_type('resource')

    def clean_service(self):
        return self._check_type('service')

    def clean_label(self):
        return self._check_type('label')

    def clean_ows_service(self):
        return self._check_type('ows_service')

    def clean_service_type(self):
        return self._check_type('service_type')

    def _check_services(self):
        s = self.cleaned_data.get('service')
        st = self.cleaned_data.get('service_type')
        if st and s:
            raise forms.ValidationError("Cannot use service and service type at the same time")

    def clean(self):
        super(MetricsFilters, self).clean()
        self._check_services()


class LabelsFilterForm(CheckTypeForm):
    metric_name = forms.CharField(required=False)

    def clean_metric(self):
        return self._check_type('metric_name')


class ResourcesFilterForm(LabelsFilterForm):
    resource_type = forms.CharField(required=False)

    def clean_resource_type(self):
        return self._check_type('resource_type')


class FilteredView(View):
    # form which validates request.GET for get_queryset()
    filter_form = None

    # iterable of pairs (from model field, to key name) to map
    # fields from model to elements of output data
    fields_map = tuple()

    # key name for output ({output_name: data})
    output_name = None

    def get_filter_args(self, request):
        self.errors = None
        if not self.filter_form:
            return {}
        f = self.filter_form(data=request.GET)
        if not f.is_valid():
            self.errors = f.errors
        return f.cleaned_data

    def get(self, request, *args, **kwargs):
        qargs = self.get_filter_args(request)
        if self.errors:
            return json_response({'success': False,
                                  'status': 'errors',
                                  'errors': self.errors},
                                 status=400)
        q = self.get_queryset(**qargs)
        from_fields = [f[0] for f in self.fields_map]
        to_fields = [f[1] for f in self.fields_map]
        out = [dict(zip(to_fields, (getattr(item, f) for f in from_fields))) for item in q]
        data = {self.output_name: out,
                'success': True,
                'errors': {},
                'status': 'ok'}
        if self.output_name != 'data':
            data['data'] = {'key': self.output_name}
        return json_response(data)


class ResourcesList(FilteredView):

    filter_form = ResourcesFilterForm
    fields_map = (('id', 'id',),
                  ('type', 'type',),
                  ('name', 'name',),)

    output_name = 'resources'

    def get_queryset(self, metric_name=None,
                     resource_type=None,
                     valid_from=None,
                     valid_to=None,
                     last=None,
                     interval=None):
        q = MonitoredResource.objects.all().distinct()
        qparams = {}
        if resource_type:
            qparams['type'] = resource_type
        if metric_name:
            sm = ServiceTypeMetric.objects.filter(metric__name=metric_name)
            qparams['metric_values__service_metric__in'] = sm
        if last:
            _from = datetime.utcnow().replace(tzinfo=pytz.utc) - timedelta(seconds=last)
            if interval is None:
                interval = 60
            if not isinstance(interval, timedelta):
                interval = timedelta(seconds=interval)
            valid_from = _from
        if valid_from:
            qparams['metric_values__valid_from__gte'] = valid_from
        if valid_to:
            qparams['metric_values__valid_to__lte'] = valid_to
        if qparams:
            q = q.filter(**qparams)
        return q


class LabelsList(FilteredView):

    filter_form = LabelsFilterForm
    fields_map = (('id', 'id',),
                  ('name', 'name',),)
    output_name = 'labels'

    def get_queryset(self, metric_name, valid_from, valid_to, interval=None, last=None):
        q = MetricLabel.objects.all().distinct()
        qparams = {}
        if metric_name:
            sm = ServiceTypeMetric.objects.filter(metric__name=metric_name)
            qparams['metric_values__service_metric__in'] = sm
        if last:
            _from = datetime.utcnow().replace(tzinfo=pytz.utc) - timedelta(seconds=last)
            if interval is None:
                interval = 60
            if not isinstance(interval, timedelta):
                interval = timedelta(seconds=interval)
            valid_from = _from
        if valid_from:
            qparams['metric_values__valid_from__gte'] = valid_from
        if valid_to:
            qparams['metric_values__valid_to__lte'] = valid_to
        if qparams:
            q = q.filter(**qparams)
        return q


class OWSServiceList(FilteredView):

    fields_map = (('name', 'name',),)
    output_name = 'ows_services'

    def get_queryset(self, **kwargs):
        return OWSService.objects.all()


class MetricDataView(View):

    def get_filters(self, **kwargs):
        out = {}
        self.errors = None
        f = MetricsFilters(data=self.request.GET)
        if not f.is_valid():
            self.errors = f.errors
        else:
            out.update(f.cleaned_data)
        return out

    def get(self, *args, **kwargs):
        filters = self.get_filters(**kwargs)
        if self.errors:
            return json_response({'status': 'error',
                                  'success': False,
                                  'errors': self.errors},
                                 status=400)
        metric_name = kwargs['metric_name']
        last = filters.pop('last', None)
        if last:
            td = timedelta(seconds=last)
            now = datetime.utcnow().replace(tzinfo=pytz.utc)
            filters['valid_from'] = now - td
            filters['valid_to'] = now
        out = capi.get_metrics_for(metric_name, **filters)
        return json_response({'data': out})


class ExceptionsListForm(CheckTypeForm):
    error_type = forms.CharField(required=False)
    service_name = forms.CharField(required=False)
    service_type = forms.CharField(required=False)
    resource = forms.CharField(required=False)

    def clean_resource(self):
        return self._check_type('resource')

    def clean_service(self):
        return self._check_type('service')


class ExceptionsListView(FilteredView):
    filter_form = ExceptionsListForm
    fields_map = (('id', 'id',),
                  ('created', 'created',),
                  ('url', 'url',),
                  ('service_data', 'service',),
                  ('error_type', 'error_type',),)

    output_name = 'exceptions'

    def get_queryset(self, error_type=None,
                     valid_from=None,
                     valid_to=None,
                     interval=None,
                     last=None,
                     service_name=None,
                     service_type=None,
                     resource=None):
        q = ExceptionEvent.objects.all().select_related()
        if error_type:
            q = q.filter(error_type=error_type)
        if last:
            _from = datetime.utcnow().replace(tzinfo=pytz.utc) - timedelta(seconds=last)
            if interval is None:
                interval = 60
            if not isinstance(interval, timedelta):
                interval = timedelta(seconds=interval)
            valid_from = _from
        if valid_from:
            q = q.filter(created__gte=valid_from)
        if valid_to:
            q = q.filter(created__lte=valid_to)
        if service_name:
            q = q.filter(service__name=service_name)
        if service_type:
            q = q.filter(service__service_type__name=service_type)
        if resource:
            q = q.filter(request__resources__in=(resource,))
        return q


class ExceptionDataView(View):

    def get_object(self, exception_id):
        try:
            return ExceptionEvent.objects.get(id=exception_id)
        except ExceptionEvent.DoesNotExist:
            return

    def get(self, request, exception_id, *args, **kwargs):
        e = self.get_object(exception_id)
        if not e:
            return json_response(errors={'exception_id': "Object not found"}, status=404)
        data = e.expose()
        return json_response(data)


class BeaconView(View):

    def get(self, request, *args, **kwargs):
        service = kwargs.get('exposed')
        if not service:
            data = [{'name': s, 'url': reverse('monitoring:api_beacon_exposed', args=(s,))} for s in exposes.keys()]
            return json_response({'exposed': data})
        try:
            ex = exposes[service]()
        except KeyError:
            return json_response(errors={'exposed': 'No service for {}'.format(service)}, status=404)
        out = {'data': ex.expose(),
               'timestamp': datetime.utcnow().replace(tzinfo=pytz.utc)}
        return json_response(out)


def index(request):
    if request.user.is_superuser:
        return render(request, 'monitoring/index.html')
    return render(request, 'monitoring/non_superuser.html')


class NotificaitonCheckForm(forms.ModelForm):
    class Meta:
        model = NotificationCheck
        fields = ('name', 'description', 'severity', 'user_threshold',)


class MetricNotificationCheckForm(forms.ModelForm):

    metric = forms.CharField(required=True)
    service = forms.CharField(required=False)
    resource = forms.CharField(required=False)
    label = forms.CharField(required=False)
    ows_service = forms.CharField(required=False)

    class Meta:
        model = MetricNotificationCheck
        fields = ('notification_check', 'min_value', 'max_value', 'max_timeout',)

    def _get_clean_model(self, cls, name):
        val = self.cleaned_data.get(name)
        if not self.fields[name].required:
            if not val:
                return
        try:
            return cls.objects.get(name=val)
        except cls.DoesNotExist:
            raise forms.ValidationError("Invalid {}: {}".format(name, val))

    def clean_metric(self):
        return self._get_clean_model(Metric, 'metric')

    def clean_service(self):
        return self._get_clean_model(Service, 'service')

    def clean_label(self):
        return self._get_clean_model(MetricLabel, 'label')

    def clean_ows_service(self):
        return self._get_clean_model(OWSService, 'ows_service')

    def clean_resource(self):
        val = self.cleaned_data.get('resource')
        if not val:
            return
        try:
            vtype, vname = val.split('=')
        except IndexError:
            raise forms.ValidationError("Invalid resource name: {}".format(val))
        try:
            return MonitoredResource.objects.get(name=vname, type=vtype)
        except MonitoredResource.DoesNotExist:
            raise forms.ValidationError("Invalid resource: {}".format(val))


class UserNotificationConfigView(View):

    def get_object(self):
        pk = self.kwargs['pk']
        return NotificationCheck.objects.get(pk=pk)

    def get(self, request, *args, **kwargs):
        out = {'success': False, 'status': 'error', 'data': [], 'errors': {}}
        status = 500
        fields = ('field_name',
                  'steps',
                  'current_value',
                  'steps_calculated',
                  'unit',
                  'is_enabled',)
        if request.user.is_authenticated():
            obj = self.get_object()
            out['success'] = True
            out['status'] = 'ok'
            form = obj.get_user_form()
            fields = [dump(r, fields) for r in obj.definitions.all()]
            out['data'] = {'form': form.as_table(),
                           'fields': fields,
                           'emails': obj.emails,
                           'notification': dump(obj)}
            status = 200
        else:
            out['errors']['user'] = ['User is not authenticated']
            status = 401
        return json_response(out, status=status)

    def post(self, request, *args, **kwargs):
        out = {'success': False, 'status': 'error', 'data': [], 'errors': {}}
        status = 500
        if request.user.is_authenticated():
            obj = self.get_object()
            try:
                is_json = True
                data = json.loads(request.body)
            except (TypeError, ValueError,):
                is_json = False
                data = request.POST.copy()

            try:
                configs = obj.process_user_form(data, is_json=is_json)
                out['success'] = True
                out['status'] = 'ok'
                out['data'] = [dump(c) for c in configs]
                status = 200
            except forms.ValidationError, err:
                out['errors'] = err.errors
                status = 400
        else:
            out['errors']['user'] = ['User is not authenticated']
            status = 401
        return json_response(out, status=status)

    if settings.MONITORING_DISABLE_CSRF:
        post = csrf_exempt(post)


class NotificationsList(FilteredView):
    filter_form = None
    fields_map = (('id', 'id',),
                  ('url', 'url',),
                  ('name', 'name',),
                  ('active', 'active',),
                  ('severity', 'severity',),
                  ('description', 'description',),
                  )

    output_name = 'data'

    def get_filter_args(self, *args, **kwargs):
        self.errors = {}
        if not self.request.user.is_authenticated():
            self.errors = {'user': ['User is not authenticated']}
        return {}

    def get_queryset(self, *args, **kwargs):
        return NotificationCheck.objects.all()

    def create(self, request, *args, **kwargs):
        f = NotificaitonCheckForm(data=request.POST)
        if f.is_valid():
            d = f.cleaned_data
            return NotificationCheck.create(**d)
        self.errors = f.errors

    def post(self, request, *args, **kwargs):
        out = {'success': False, 'status': 'error', 'data': [], 'errors': {}}
        d = self.create(request, *args, **kwargs)
        if d is None:
            out['errors'] = self.errors
            status = 400
        else:
            out['data'] = dump(d)
            out['success'] = True
            out['status'] = 'ok'
            status = 200
        return json_response(out, status=status)


class StatusCheckView(View):
    fields = ('name', 'severity',
              'offending_value',
              'threshold_value',
              'spotted_at',
              'valid_from',
              'valid_to',
              'check_url',
              'check_id',
              'description',
              'message',)

    def get(self, request, *args, **kwargs):
        capi = CollectorAPI()
        checks = capi.get_notifications()
        data = {'status': 'ok', 'success': True, 'data': {}}
        d = data['data']
        d['problems'] = problems = []
        d['health_level'] = 'ok'
        _levels = ('fatal', 'error', 'warning',)
        levels = set([])

        for nc, ncdata in checks:
            for ncd in ncdata:
                levels.add(ncd.severity)
                problems.append(dump(ncd, self.fields))
        if levels:
            for l in _levels:
                if l in levels:
                    d['health_level'] = l
                    break

        return json_response(data)


class AutoconfigureView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            out = {'success': False,
                   'status': 'error',
                   'errors': {'user': ['User is not authenticated']}
                   }
            return json_response(out, status=401)
        if not (request.user.is_superuser or request.user.is_staff):
            out = {'success': False,
                   'status': 'error',
                   'errors': {'user': ['User is not permitted']}
                   }
            return json_response(out, status=401)
        do_autoconfigure()
        out = {'success': True,
               'status': 'ok',
               'errors': {}
               }
        return json_response(out)


api_metrics = MetricsList.as_view()
api_services = ServicesList.as_view()
api_hosts = HostsList.as_view()
api_labels = LabelsList.as_view()
api_resources = ResourcesList.as_view()
api_ows_services = OWSServiceList.as_view()
api_metric_data = MetricDataView.as_view()
api_exceptions = ExceptionsListView.as_view()
api_exception = ExceptionDataView.as_view()
api_beacon = BeaconView.as_view()

api_user_notification_config = UserNotificationConfigView.as_view()
api_user_notifications = NotificationsList.as_view()
api_status = StatusCheckView.as_view()
api_autoconfigure = AutoconfigureView.as_view()
