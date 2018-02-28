# -*- coding:utf-8 -*-
from ..saas.importers import BaseImporter
from .validators import *
from ..saas.validators import field_position
from django_szuprefix.utils import datautils

__author__ = 'denishuang'


def format_class_grade(d):
    from .helper import normalize_clazz_name
    v = d.get(field_class.name)
    g = d.get(field_grade.name)
    if v and g:
        d[field_class.name] = normalize_clazz_name(v, g)[0]


class StudentImporter(BaseImporter):
    fields = [
        field_han_name,
        field_student_number,
        MobileField(synonyms=[u"学生手机号"]),
        field_weixinid,
        field_email,
        field_qq,
        field_college,
        field_major,
        field_grade,
        field_class,
        field_idcard,
        field_instructor,
        field_counsellor,
    ]
    min_fields_count = 3
    key_field = field_student_number
    required_fields = [field_student_number, field_mobile]
    extra_cleans = [format_class_grade]

    def import_one(self, api, d):
        wx_userid = d.get(u"学号")
        department_path = u"%s/%s/%s" % (d.get(u"院系"), d.get(u"年级"), d.get(u"班级"))
        department, created = api.get_or_create_department_by_path(department_path)
        worker, created = api.corp.workers.update_or_create(wx_userid=wx_userid,
                                                            defaults=dict(
                                                                mobile=d.get(u"手机"),
                                                                position=u'学生',
                                                                gender={u"男": 1, u"女": 2}.get(d.get(u"性别"), 0),
                                                                name=d.get(u"姓名"),
                                                                email=d.get(u"邮箱"),
                                                                weixinid=d.get(u"微信号")
                                                            ))
        worker.update_extattr(datautils.exclude_dict_keys(d, u"微信号", u"邮箱", u"手机", u"姓名", u"性别"))
        worker.departments = [department]
        return worker, created

    def extra_action(self, api, worker, created):
        ur = api.upload_worker(worker)
        return ur.get("errcode") == 0 or ur


def bind_worker_number_to_pinyin_name(d):
    worker_number, e = d.get(u"工号")
    if not worker_number:
        name, e2 = d.get(u"姓名")
        from unidecode import unidecode
        d[u"工号"] = (unidecode(name).replace(" ", ""), [])
        d.warnings.append("自动根据姓名生成工号")


class TeacherImporter(BaseImporter):
    fields = [
        field_han_name,
        field_worker_number,
        field_mobile,
        field_weixinid,
        field_email,
        field_department,
        field_position,
        field_is_instructor,
        field_is_counsellor,
    ]
    min_fields_count = 3

    extra_cleans = [bind_worker_number_to_pinyin_name]

    def import_one(self, api, d):
        wx_userid = d.get(u"工号")
        department_path = u"%s" % d.get(u"部门", u"未指定部门")
        department = api.corp.departments.filter(name=department_path).first()
        if not department:
            department, created = api.get_or_create_department_by_path(department_path)
        worker, created = api.corp.workers.update_or_create(wx_userid=wx_userid,
                                                            defaults=dict(
                                                                mobile=d.get(u"手机"),
                                                                position=d.get(u"职位", u"教师"),
                                                                gender={u"男": 1, u"女": 2}.get(d.get(u"性别"), 0),
                                                                name=d.get(u"姓名"),
                                                                email=d.get(u"邮箱"),
                                                                weixinid=d.get(u"微信号")
                                                            ))
        worker.update_extattr(datautils.exclude_dict_keys(d, u"微信号", u"邮箱", u"手机", u"部门", u"职位", u"姓名", u"性别"))
        worker.departments = [department]
        return worker, created

    def extra_action(self, api, worker, created):
        ur = api.upload_worker(worker)
        return ur.get("errcode") == 0 or ur
