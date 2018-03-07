# -*- coding:utf-8 -*- 
__author__ = 'denishuang'
from . import models
from django.db.models.fields import NOT_PROVIDED


def init_person(worker):
    profile = worker.profile
    fns = "email,mobile,id_card,gender,ethnic,city".split(",")
    fs = [f for f in models.Person._meta.local_fields if f.name in fns]
    ps = dict([(f.name, profile.get(f.verbose_name, f.default != NOT_PROVIDED and f.default or None)) for f in fs])
    ps['name'] = worker.name
    person, created = models.Person.objects.update_or_create(
        user=worker.user,
        defaults=ps)
