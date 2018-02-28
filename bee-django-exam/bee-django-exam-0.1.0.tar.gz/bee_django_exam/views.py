#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import json, qrcode, os, shutil, urllib
from django.shortcuts import get_object_or_404, reverse, redirect, render
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Sum, Count
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.utils.datastructures import MultiValueDict
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from django.utils.six import BytesIO
from django.apps import apps
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django import forms

from .decorators import cls_decorator, func_decorator
from .models import Grade, Notice, UserExamRecord, GradeCertField
from .forms import GradeForm, NoticeForm, UserExamRecordCreateForm, UserExamRecordUpdateForm, GradeCertFieldForm, \
    UserExamRecordCertUploadForm, UserExamNoticeForm
from .exports import before_user_exam, after_user_exam_add, after_user_passed
from .utils import get_cert_field_name, JSONResponse, Cert, check_user_record, get_user, get_user_name


# Create your views here.
def test(request):
    return


# ========grade===========
@method_decorator(cls_decorator(cls_name='GradeList'), name='dispatch')
class GradeList(ListView):
    model = Grade
    template_name = 'bee_django_exam/grade/grade_list.html'
    context_object_name = 'grade_list'
    paginate_by = 20


@method_decorator(cls_decorator(cls_name='GradeDetail'), name='dispatch')
class GradeDetail(DetailView):
    model = Grade
    template_name = 'bee_django_exam/grade/grade_detail.html'
    context_object_name = 'grade'


@method_decorator(cls_decorator(cls_name='GradeCreate'), name='dispatch')
class GradeCreate(CreateView):
    model = Grade
    form_class = GradeForm
    template_name = 'bee_django_exam/grade/grade_form.html'
    success_url = reverse_lazy('bee_django_exam:grade_list')


@method_decorator(cls_decorator(cls_name='GradeUpdate'), name='dispatch')
class GradeUpdate(UpdateView):
    model = Grade
    form_class = GradeForm
    template_name = 'bee_django_exam/grade/grade_form.html'
    success_url = reverse_lazy('bee_django_exam:grade_list')

    # def get_context_data(self, **kwargs):
    #     context = super(GradeUpdate, self).get_context_data(**kwargs)
    #     grade_id = self.kwargs["pk"]
    #     grade = Grade.objects.get(id=grade_id)
    #     context["cert"] = grade.cert_image
    #     return context


@method_decorator(cls_decorator(cls_name='GradeDelete'), name='dispatch')
class GradeDelete(DeleteView):
    model = Grade
    success_url = reverse_lazy('bee_django_exam:grade_list')

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)


@method_decorator(cls_decorator(cls_name='GradeCertFieldCreate'), name='dispatch')
class GradeCertFieldCreate(CreateView):
    model = GradeCertField
    form_class = GradeCertFieldForm
    template_name = 'bee_django_exam/grade/cert/cert_field_form.html'
    success_url = None

    # def get_cert_img(self):


    def get_context_data(self, **kwargs):
        context = super(GradeCertFieldCreate, self).get_context_data(**kwargs)
        grade_id = self.kwargs["pk"]
        grade = Grade.objects.get(id=grade_id)
        context["grade"] = grade
        return context

    def form_valid(self, form):
        f = form.save(commit=False)
        grade_id = self.kwargs["pk"]
        grade = Grade.objects.get(id=grade_id)
        field_name = get_cert_field_name(form.cleaned_data['field'])
        f.name = field_name
        f.grade = grade
        f.save()
        self.success_url = reverse_lazy("bee_django_exam:grade_detail", kwargs=self.kwargs)
        return super(GradeCertFieldCreate, self).form_valid(form)


@method_decorator(cls_decorator(cls_name='GradeCertFieldCreate'), name='dispatch')
class GradeCertFieldUpdate(UpdateView):
    model = GradeCertField
    form_class = GradeCertFieldForm
    template_name = 'bee_django_exam/grade/cert/cert_field_form.html'
    success_url = None

    def form_valid(self, form):
        field_id = self.kwargs["pk"]
        grade = Grade.objects.get(gradecertfield__id=field_id)
        self.success_url = reverse_lazy("bee_django_exam:grade_detail", kwargs={"pk": grade.id})
        return super(GradeCertFieldUpdate, self).form_valid(form)


@method_decorator(cls_decorator(cls_name='GradeCertFieldDelete'), name='dispatch')
class GradeCertFieldDelete(DeleteView):
    model = GradeCertField
    success_url = reverse_lazy('bee_django_exam:grade_list')

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)


@method_decorator(cls_decorator(cls_name='GradeCertModify'), name='dispatch')
class GradeCertModify(DetailView):
    model = Grade
    template_name = 'bee_django_exam/grade/cert/cert_modify.html'
    context_object_name = 'grade'

    def get_context_data(self, **kwargs):
        context = super(GradeCertModify, self).get_context_data(**kwargs)
        grade_id = self.kwargs["pk"]
        grade = Grade.objects.get(id=grade_id)
        res, msg, cert_path = Cert().create_cert(grade=grade, record=None)
        print(msg)
        print(res, msg, cert_path)
        context["cert_path"] = cert_path
        return context


# ========notice===========
@method_decorator(cls_decorator(cls_name='NoticeList'), name='dispatch')
class NoticeList(ListView):
    model = Notice
    template_name = 'bee_django_exam/notice/notice_list.html'
    context_object_name = 'notice_list'
    paginate_by = 20


@method_decorator(cls_decorator(cls_name='NoticeDetail'), name='dispatch')
class NoticeDetail(DetailView):
    model = Notice
    template_name = 'bee_django_exam/notice/notice_detail.html'
    context_object_name = 'notice'


@method_decorator(cls_decorator(cls_name='NoticeCreate'), name='dispatch')
class NoticeCreate(CreateView):
    model = Notice
    form_class = NoticeForm
    template_name = 'bee_django_exam/notice/notice_form.html'
    success_url = reverse_lazy('bee_django_exam:notice_list')


@method_decorator(cls_decorator(cls_name='NoticeUpdate'), name='dispatch')
class NoticeUpdate(UpdateView):
    model = Notice
    form_class = NoticeForm
    template_name = 'bee_django_exam/notice/notice_form.html'


@method_decorator(cls_decorator(cls_name='UserExamRecordCreate'), name='dispatch')
class UserExamRecordCreate(CreateView):
    model = UserExamRecord
    form_class = UserExamRecordCreateForm
    template_name = 'bee_django_exam/record/user_record_add.html'
    success_url = None

    def form_valid(self, form):
        record = form.save(commit=False)
        user_id = self.kwargs["user_id"]
        error = check_user_record(user_id)
        if error:
            messages.error(self.request, error)
            return redirect(reverse('bee_django_exam:user_exam_record_done'))
        # res, msg = before_user_exam(user_id)
        # if res == False:
        #     messages.error(self.request, msg)
        #     return redirect(reverse('bee_django_exam:user_exam_record_done'))
        # record = form.save(commit=False)
        # record.user_id = user_id
        # record.save()
        # record.grade_name = record.grade.name
        # record.save()
        # res, msg = after_user_exam_add(record)
        # messages.success(self.request, "报名成功")
        return redirect(
            reverse('bee_django_exam:user_exam_notice', kwargs={"user_id": user_id, "grade_id": record.grade_id}))


@method_decorator(cls_decorator(cls_name='UserExamNotice'), name='dispatch')
class UserExamNotice(TemplateView):
    template_name = "bee_django_exam/record/notice_detail.html"

    def get_context_data(self, **kwargs):
        context = super(UserExamNotice, self).get_context_data(**kwargs)
        grade_id = self.kwargs["grade_id"]
        grade = Grade.objects.get(id=grade_id)
        context["form"] = UserExamNoticeForm()
        context["grade"] = grade
        context["user_id"] = self.kwargs["user_id"]
        return context

    def post(self, request, *args, **kwargs):
        form = UserExamNoticeForm(request.POST)
        if form.is_valid():
            user_id = self.kwargs["user_id"]
            grade_id = self.kwargs["grade_id"]
            error = check_user_record(user_id)
            if error:
                messages.error(self.request, error)
                return redirect(reverse('bee_django_exam:user_exam_record_done'))
            res, msg = before_user_exam(user_id)
            if res == False:
                messages.error(self.request, msg)
                return redirect(reverse('bee_django_exam:user_exam_record_done'))
            record = UserExamRecord()
            record.user_id = user_id
            grade = Grade.objects.get(id=grade_id)
            record.grade = grade
            record.grade_name = grade.name
            record.save()
            res, msg = after_user_exam_add(record)
            messages.success(self.request, "报名成功")
            return redirect(reverse('bee_django_exam:user_exam_record_done'))


@method_decorator(cls_decorator(cls_name='UserExamRecordDone'), name='dispatch')
class UserExamRecordDone(TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, 'bee_django_exam/record/record_done.html')


# 所有学生考级申请记录
@method_decorator(cls_decorator(cls_name='UserAllExamRecordList'), name='dispatch')
class UserAllExamRecordList(ListView):
    model = UserExamRecord
    template_name = 'bee_django_exam/record/user_all_record_list.html'
    context_object_name = 'record_list'
    paginate_by = 20


# 某个学生自己的考级申请记录
@method_decorator(cls_decorator(cls_name='UserExamRecordList'), name='dispatch')
class UserExamRecordList(ListView):
    model = UserExamRecord
    template_name = 'bee_django_exam/record/user_record_list.html'
    paginate_by = 20
    context_object_name = 'record_list'
    queryset = None

    def get_queryset(self):
        super(UserExamRecordList, self).get_queryset()
        record_list = UserExamRecord.objects.filter(user__id=self.kwargs["user_id"])
        return record_list

    def get_context_data(self, **kwargs):
        context = super(UserExamRecordList, self).get_context_data(**kwargs)
        context["user_name"] = get_user_name(self.kwargs["user_id"])
        context["user"] = get_user(self.kwargs["user_id"])
        return context


@method_decorator(cls_decorator(cls_name='UserExamRecordDetail'), name='dispatch')
class UserExamRecordDetail(DetailView):
    model = UserExamRecord
    template_name = 'bee_django_exam/record/record_detail.html'
    context_object_name = 'record'


@method_decorator(cls_decorator(cls_name='UserExamRecordUpdate'), name='dispatch')
class UserExamRecordUpdate(UpdateView):
    model = UserExamRecord
    form_class = UserExamRecordUpdateForm
    template_name = 'bee_django_exam/record/admin_record_update.html'
    success_url = reverse_lazy("bee_django_exam:user_exam_record_list")

    def get_context_data(self, **kwargs):
        context = super(UserExamRecordUpdate, self).get_context_data(**kwargs)
        record = UserExamRecord.objects.get(id=self.kwargs["pk"])
        context["user"] = record.user
        context["grade_name"] = record.grade_name
        return context

    def form_valid(self, form):
        old_record = UserExamRecord.objects.get(id=self.kwargs["pk"])
        old_pass = old_record.is_passed
        new_pass = form.cleaned_data['is_passed']
        if old_pass == False and new_pass == True:
            after_user_passed(old_record)
        self.success_url = reverse_lazy("bee_django_exam:user_exam_record_detail", kwargs=self.kwargs)
        return super(UserExamRecordUpdate, self).form_valid(form)


@method_decorator(cls_decorator(cls_name='UserCertCreate'), name='dispatch')
class UserCertCreate(TemplateView):
    def post(self, request, *args, **kwargs):
        record_id = self.kwargs["record_id"]
        record = UserExamRecord.objects.get(id=record_id)
        res, msg, cert_path = Cert().create_cert(grade=record.grade, record=record)
        return JSONResponse(json.dumps({"res": res, "msg": msg}, ensure_ascii=False))
        # return super(UserCertCreate,self).post(request, *args, **kwargs)


@method_decorator(cls_decorator(cls_name='UserCertUpload'), name='dispatch')
class UserCertUpload(CreateView):
    model = UserExamRecord
    form_class = UserExamRecordCertUploadForm
    template_name = 'bee_django_exam/record/user_record_cert_upload.html'
    success_url = None

    def form_valid(self, form):
        cert = form.cleaned_data['cert']

        self.success_url = reverse_lazy("bee_django_exam:user_exam_record_detail", kwargs=self.kwargs)
        return super(UserCertUpload, self).form_valid(form)
