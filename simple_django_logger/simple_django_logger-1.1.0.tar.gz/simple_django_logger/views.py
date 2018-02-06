from django.views.generic import View
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render
from django.http import Http404

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from .models import (
    Log,
    RequestLog,
    EventLog,
)

from .constants import Keys
from .utils import Logger
from .response import render as logger_render
from .utils import RequestLogger
from .utils import EventLogger


class AllLogs(View):
    template_name = 'logger/all_logs.html'

    def get(self, request):
        page = int(request.GET.get(Keys.PAGE, 1))
        show = int(request.GET.get(Keys.SHOW, 10))

        logs = Log.objects.all().order_by('-created_on')

        # Check the url filter
        url = request.GET.get(Keys.URL, '')
        if url:
            logs = logs.filter(request_url__icontains=url)

        # Check the log level filter
        log_level = request.GET.get(Keys.LOG_LEVEL, Keys.ALL).upper().strip()
        if log_level == Keys.ERROR:
            logs = logs.filter(log_level=Log.ERROR)
        elif log_level == Keys.DEBUG:
            logs = logs.filter(log_level=Log.DEBUG)
        elif log_level == Keys.WARN:
            logs = logs.filter(log_level=Log.WARN)
        elif log_level == Keys.INFO:
            logs = logs.filter(log_level=Log.INFO)

        # Check for the the request method
        method = request.GET.get(Keys.REQUEST_METHOD, '')
        if method:
            logs = logs.filter(request_method=method.upper())

        paginator = Paginator(logs, show)

        try:
            logs = paginator.page(page)
        except EmptyPage:
            logs = paginator.page(paginator.num_pages)

        if logs.has_next():
            next_url = 'page=%d&show=%s&url=%s&level=%s&method=%s' % (
                page + 1, show, url, log_level, method)
        else:
            next_url = None

        if logs.has_previous():
            prev_url = 'page=%d&show=%s&url=%s&level=%s&method=%s' % (
                page - 1, show, url, log_level, method)
        else:
            prev_url = None

        context = {
            'logs': logs,
            'log_levels': Log.LOG_LEVELS,
            'next_url': next_url,
            'prev_url': prev_url,
            'log_level': log_level,
            'method': method,
            'url': url}
        return render(request, self.template_name, context)

    def post(self, request):
        Log.objects.all().delete()
        return HttpResponseRedirect(reverse('logger:all_logs'))


class SingleLog(View):
    template_name = 'logger/log.html'

    def get(self, request, log_id):
        try:
            log = Log.objects.get(id=log_id)
        except Log.DoesNotExist:
            raise Http404

        context = {
            'log': log,
            'log_levels': Log.LOG_LEVELS}
        return render(request, self.template_name, context)

    def post(self, request, log_id):
        try:
            Log.objects.get(id=log_id).delete()
        except Log.DoesNotExist:
            raise Http404
        return HttpResponseRedirect(reverse('logger:all_logs'))


class AllRequestLogs(View):
    template_name = 'logger/all_request_logs.html'

    def get(self, request):
        page = int(request.GET.get('page', 1))
        show = int(request.GET.get(Keys.SHOW, 10))

        logs = RequestLog.objects.all().order_by('-created_on')

        # Check the url filter
        url = request.GET.get(Keys.URL, '')
        if url:
            logs = logs.filter(url__icontains=url)

        # Check for the the request method
        method = request.GET.get(Keys.REQUEST_METHOD, '')
        if method:
            logs = logs.filter(method=method.upper())

        # Check for the the request method
        status = request.GET.get(Keys.RESPONSE_STATUS, '')
        try:
            status = int(status)
        except Exception:
            status = None
        if status:
            logs = logs.filter(
                response_status__gte=status,
                response_status__lt=(status + 100))

        paginator = Paginator(logs, show)

        try:
            logs = paginator.page(page)
        except EmptyPage:
            logs = paginator.page(paginator.num_pages)

        if logs.has_next():
            next_url = 'page=%d&show=%s&url=%s&status=%s&method=%s' % (
                page + 1, show, url, status, method)
        else:
            next_url = None

        if logs.has_previous():
            prev_url = 'page=%d&show=%s&url=%s&status=%s&method=%s' % (
                page - 1, show, url, status, method)
        else:
            prev_url = None

        context = {
            'logs': logs,
            'next_url': next_url,
            'prev_url': prev_url,
            'status': status,
            'method': method,
            'url': url}
        return render(request, self.template_name, context)

    def post(self, request):
        RequestLog.objects.all().delete()
        return HttpResponseRedirect(reverse('logger:all_request_logs'))


class SingleRequestLog(View):
    template_name = 'logger/request_log.html'

    def get(self, request, log_id):
        try:
            log = RequestLog.objects.get(id=log_id)
        except RequestLog.DoesNotExist:
            raise Http404

        context = {
            'log': log}
        return render(request, self.template_name, context)

    def post(self, request, log_id):
        try:
            RequestLog.objects.get(id=log_id).delete()
        except RequestLog.DoesNotExist:
            raise Http404
        return HttpResponseRedirect(reverse('logger:all_request_logs'))


class AllEventLogs(View):
    template_name = 'logger/all_event_logs.html'

    def get(self, request):
        page = int(request.GET.get(Keys.PAGE, 1))
        show = int(request.GET.get(Keys.SHOW, 10))

        logs = EventLog.objects.all().order_by('-created_on')

        # Check the tag filter
        tag = request.GET.get(Keys.TAG, '')
        if tag:
            logs = logs.filter(tag__icontains=tag)

        # Check the log level filter
        log_level = request.GET.get(Keys.LOG_LEVEL, Keys.ALL).upper()
        if log_level == Keys.ERROR:
            logs = logs.filter(log_level=EventLog.ERROR)
        elif log_level == Keys.DEBUG:
            logs = logs.filter(log_level=EventLog.DEBUG)
        elif log_level == Keys.WARN:
            logs = logs.filter(log_level=EventLog.WARN)
        elif log_level == Keys.INFO:
            logs = logs.filter(log_level=EventLog.INFO)

        # Check for the the message
        message = request.GET.get(Keys.MESSAGE, '')
        if message:
            logs = logs.filter(message__icontains=message)

        paginator = Paginator(logs, show)

        try:
            logs = paginator.page(page)
        except EmptyPage:
            logs = paginator.page(paginator.num_pages)

        if logs.has_next():
            next_url = 'page=%d&level=%s&tag=%s&message=%s' % (
                page + 1, log_level, tag, message)
        else:
            next_url = None

        if logs.has_previous():
            prev_url = 'page=%d&level=%s&tag=%s&message=%s' % (
                page - 1, log_level, tag, message)
        else:
            prev_url = None

        context = {
            'logs': logs,
            'log_levels': EventLog.LOG_LEVELS,
            'tag': tag,
            'log_level': log_level,
            'message': message,
            'next_url': next_url,
            'prev_url': prev_url}
        return render(request, self.template_name, context)

    def post(self, request):
        EventLog.objects.all().delete()
        return HttpResponseRedirect(reverse('logger:all_event_logs'))


class TestLogs(View):
    template_name = 'logger/logger_test.html'

    def get(self, request):
        logs = [
            Logger.log_info(request, 'Some info message. For Django render.'),
            Logger.log_debug(request, 'Some debug message. For Django render.'),
            Logger.log_warn(request, 'Some warn message. For Django render.'),
        ]

        context = {'some': 'data'}
        return logger_render(request, self.template_name, context, logs=logs)


class TestRequestLogs(View):
    template_name = 'logger/logger_test.html'

    def get(self, request):
        response = RequestLogger.get(
            'https://jsonplaceholder.typicode.com/posts/1',
            params={'query': 'value'},
            user=request.user,
            message='Some post request message')
        return render(request, self.template_name, {'text': response.text})


class TestEventLogs(View):
    template_name = 'logger/logger_test.html'

    def get(self, request):
        EventLogger.log_debug('Some debug message', tag='tag1')
        EventLogger.log_error('Some error message', tag='tag2')
        EventLogger.log_info('Some info message', tag='tag3')
        EventLogger.log_warn('Some warn message', tag='tag4')

        context = {'some': 'data'}
        return render(request, self.template_name, context)
