#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import json
from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.utils.decorators import method_decorator
from .decorators import cls_decorator, func_decorator
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Sum, Count
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Message, SendRecord
from .forms import MessageForm
from .exports import get_user
from .utils import get_user_name, JSONResponse


# Create your views here.
# =======course=======
def test(request):
    from exports import send_message
    from django.contrib.auth.models import User
    to_user = User.objects.all().first()
    res = send_message(to_user=to_user, from_user=to_user, title='test', url=None)


@method_decorator(cls_decorator(cls_name='MessageList'), name='dispatch')
class MessageList(ListView):
    template_name = 'bee_django_message/message/message_list.html'
    context_object_name = 'message_list'
    paginate_by = 20
    queryset = Message.objects.all()


@method_decorator(cls_decorator(cls_name='MessageDetail'), name='dispatch')
class MessageDetail(DetailView):
    model = Message
    template_name = 'bee_django_message/message/message_detail.html'
    context_object_name = 'message'


@method_decorator(cls_decorator(cls_name='MessageCreate'), name='dispatch')
class MessageCreate(CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'bee_django_message/message/message_form.html'


@method_decorator(cls_decorator(cls_name='MessageUpdate'), name='dispatch')
class MessageUpdate(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'bee_django_message/message/message_form.html'


@method_decorator(cls_decorator(cls_name='MessageDelete'), name='dispatch')
class MessageDelete(DeleteView):
    model = Message
    success_url = reverse_lazy('bee_django_message:message_list')

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)


# 发送记录
@method_decorator(cls_decorator(cls_name='UserRecordList'), name='dispatch')
class UserRecordList(ListView):
    template_name = 'bee_django_message/record/user_record_list.html'
    context_object_name = 'record_list'
    paginate_by = 20
    queryset = None

    def get_queryset(self):
        user = get_user(self.request)
        self.queryset = SendRecord.objects.filter(to_user=user)
        return self.queryset

    def get_context_data(self, **kwargs):
        user = get_user(self.request)
        context = super(UserRecordList, self).get_context_data(**kwargs)
        context['user_name'] = get_user_name(user)
        return context

#
# @method_decorator(cls_decorator(cls_name='RecordDetail'), name='dispatch')
# class RecordDetail(DetailView):
#     model = SendRecord
#     template_name = 'bee_django_message/message/message_detail.html'
#     context_object_name = 'record'


@method_decorator(cls_decorator(cls_name='UserRecordClick'), name='dispatch')
class UserRecordClick(TemplateView):
    def post(self, request, *args, **kwargs):
        record_id = request.POST.get("record_id")
        record = SendRecord.objects.get(id=record_id)
        record.is_view = True
        record.save()
        return JSONResponse(json.dumps({"url": record.url}, ensure_ascii=False))
