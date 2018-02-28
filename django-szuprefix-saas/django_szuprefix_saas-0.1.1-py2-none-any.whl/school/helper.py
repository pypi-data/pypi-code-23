# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import datetime
import unidecode
from django.db.models import NOT_PROVIDED, ForeignKey
from django_szuprefix.utils import dateutils
from . import choices, models
import re


def gen_default_grades(school):
    gs = choices.MAP_SCHOOL_TYPE_GRADES.get(school.type)
    if not gs:
        return
    for number, name in gs:
        school.grades.create(name=name, number=number)


def gen_default_session(school, offset=0):
    today = dateutils.format_the_date()
    year = today.month >= 8 and today.year or today.year - 1
    year -= offset
    return school.sessions.get_or_create(
        number=year,
        defaults=dict(
            name="%s届" % year,
            begin_date="%s-09-01" % year,
            end_date="%s-07-01" % (year + 1))
    )


RE_CLAZZ_GRADE_NAME = re.compile(r"^(\d{4}|\d{2})级*")


def normalize_clazz_name(clazz_name, grade=None):
    m = RE_CLAZZ_GRADE_NAME.search(clazz_name)
    if m:
        g = m.group(0)
        clazz_name = clazz_name[m.pos + len(g):]
        if not clazz_name:
            clazz_name = g[2:]
            g = g[:2]
        g = "%s级" % grade_name_to_number(g)
        if not grade:
            grade = g
        grade = normalize_grade_name(grade, g)
    if not clazz_name.endswith("班"):
        clazz_name = "%s班" % clazz_name
    return "%s%s" % (grade, clazz_name), clazz_name, grade


def normalize_grade_name(grade, default=None):
    from datetime import datetime
    maxgrade = "%d级" % datetime.now().year
    if len(grade) == len(maxgrade) and grade > maxgrade:
        grade = default
    if grade[-1] != "级":
        grade += "级"
    return grade


RE_MAJOR = re.compile(ur"([^\(\)]*)(\(([^\(\)]*)\)|)")


def normalize_major_name(major):
    major = major.replace(" ", "").replace("（", "(").replace("）", ")")
    m = RE_MAJOR.search(major)
    if m:
        return m.group(1), m.group(3)
    return major, None


RE_GRADE = re.compile(ur"(\d+)[级]*")


def grade_name_to_number(grade_name):
    m = RE_GRADE.search(grade_name)
    if m:
        no = int(m.group(1))
        if no < 50:
            no += 2000
        elif no < 100:
            no += 1900
        return no


def cur_grade_number(grade_name, today=None):
    """
     when today is 2016.9.10

     cur_grade_number("14级")
     3
     cur_grade_number("2015级")
     2
     cur_grade_number("2016级")
     1
     cur_grade_number("98级")
     19
     cur_grade_number("17级")
     0
     cur_grade_number("18级")
     -1
    """
    gno = grade_name_to_number(grade_name)
    if not gno:
        return
    today = today or datetime.date.today()
    num = today.year - gno
    if today.month >= 8:
        num += 1
    return num


def cur_grade_year(grade_num, today=None):
    today = today or datetime.date.today()
    year = today.year - grade_num
    if today.month >= 8:
        year += 1
    return year


def cur_grade_name(grade_num, today=None):
    return "%s级" % cur_grade_year(grade_num, today)


def get_cur_term(corp):
    from django_szuprefix.utils.dateutils import format_the_date
    today = format_the_date()
    year = today.month >= 8 and today.year or today.year - 1
    month = today.month
    day = today.day
    part = (month * 100 + day < 215 or month >= 8) and 1 or 2
    name = "%s-%s学年第%s学期" % (year, year + 1, part == 1 and "一" or "二")
    start_date = datetime.date(today.year, part == 1 and 9 or 3, 1)
    term, created = corp.school_terms.get_or_create(year=year,
                                                    part=part,
                                                    defaults=dict(name=name,
                                                                  start_date=start_date))
    return term


def init_student(worker):
    profile = worker.profile
    party = worker.party
    school = party.as_school

    def get_field_value_from_profile(profile, fs):
        r = {}
        for f in fs:
            if isinstance(f, (ForeignKey)):
                fo, created = f.related_model.objects.get_or_create(school=school, name=profile.get(f.verbose_name))
                r[f.name] = fo
            else:
                r[f.name] = profile.get(f.verbose_name, f.default != NOT_PROVIDED and f.default or None)
        return r

    grade_name = profile.get('年级')
    grade_number = cur_grade_number(grade_name)
    grade, created = school.grades.get_or_create(number=grade_number)
    session_number = grade_name_to_number(grade_name)
    session, created = school.sessions.get_or_create(number=session_number)
    fns = "number,name".split(",")
    fs = [f for f in models.Student._meta.local_fields if f.name in fns]
    ps = get_field_value_from_profile(profile, fs)
    grade = grade
    clazz_name = profile.get('班级')
    clazz, created = school.clazzs.get_or_create(
        name=clazz_name,
        grade=grade,
        number=unidecode.unidecode(clazz_name).replace(" ", ""),
        defaults=dict(entrance_session=session)
    )
    ps['clazz'] = clazz
    ps['entrance_session'] = session
    ps['grade'] = grade
    student, created = school.students.update_or_create(
        user=worker.user,
        defaults=ps)
