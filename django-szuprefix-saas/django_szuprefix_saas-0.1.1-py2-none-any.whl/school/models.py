# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from django_szuprefix.utils import modelutils, datautils
from . import choices
from django_szuprefix_saas.saas.models import Party
from django.contrib.auth.models import User


class School(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "学校"

    party = models.OneToOneField(Party, verbose_name=Party._meta.verbose_name, related_name="as_school")
    name = models.CharField("名称", max_length=128, unique=True)
    type = models.PositiveSmallIntegerField("类别", choices=choices.CHOICES_SCHOOL_TYPE,
                                            default=choices.SCHOOL_TYPE_PRIMARY)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    modify_time = models.DateTimeField("修改时间", auto_now=True)
    settings = GenericRelation("common.Setting")

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        if self.party_id is None:
            self.party = Party.objects.create(name=self.name)
        return super(School, self).save(**kwargs)


class Teacher(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "老师"

    school = models.ForeignKey(School, verbose_name=School._meta.verbose_name, related_name="teachers",
                               on_delete=models.PROTECT)
    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="school_teachers", blank=True,
                              on_delete=models.PROTECT)
    user = models.OneToOneField(User, verbose_name="网站用户", null=True, related_name="as_school_teacher")
    name = models.CharField("姓名", max_length=32, null=True, blank=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    modify_time = models.DateTimeField("修改时间", auto_now=True)

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        self.party = self.school.party
        if not self.user:
            self.user = self.party.workers.create(name=self.name, position=self._meta.verbose_name).user
        return super(Teacher, self).save(**kwargs)

    def as_user(self):
        return self.user


class Session(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "届别"
        unique_together = ('school', 'number')
        ordering = ('school', 'number')

    school = models.ForeignKey(School, verbose_name=School._meta.verbose_name, related_name="sessions",
                               on_delete=models.PROTECT)
    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="school_sessions", blank=True,
                              on_delete=models.PROTECT)
    number = models.CharField("编号", max_length=16, db_index=True)
    name = models.CharField("名称", max_length=64, db_index=True, blank=True)
    begin_date = models.DateField("开始日期", blank=True)
    end_date = models.DateField("结束日期", blank=True)

    def save(self, **kwargs):
        self.party = self.school.party
        if not self.name:
            self.name = "%s届" % self.number
        if not self.begin_date:
            self.begin_date = "%s-08-01" % self.number
        if not self.end_date:
            self.end_date = "%s-07-31" % (int(self.number) + 1)
        return super(Session, self).save(**kwargs)

    def __unicode__(self):
        return self.name


class Grade(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "年级"
        unique_together = ('school', 'number')
        ordering = ('school', 'number')

    school = models.ForeignKey(School, verbose_name=School._meta.verbose_name, related_name="grades",
                               on_delete=models.PROTECT)
    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="school_grades", blank=True,
                              on_delete=models.PROTECT)
    number = models.PositiveSmallIntegerField("编号", default=1)
    name = models.CharField("名称", max_length=64, db_index=True, blank=True)
    clazz_count = models.PositiveSmallIntegerField("班数", default=3)

    def save(self, **kwargs):
        self.party = self.school.party
        if not self.name:
            n = self.number
            self.name = n <= 10 and '%s年级' % "零一二三四五六七八九十"[self.number] or '%d级' % n
        return super(Grade, self).save(**kwargs)

    def __unicode__(self):
        return self.name


class College(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "院系"
        ordering = ("school", "name")

    school = models.ForeignKey(School, verbose_name=School._meta.verbose_name, related_name="colleges",
                               on_delete=models.PROTECT)
    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="school_colleges", blank=True,
                              on_delete=models.PROTECT)
    name = models.CharField("名称", max_length=64, db_index=True)
    short_name = models.CharField("简称", max_length=64, blank=True, default="", db_index=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("修改时间", auto_now=True)

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        self.party = self.school.party
        self.short_name = self.short_name or self.name
        return super(College, self).save(**kwargs)

    @property
    def student_count(self):
        return self.students.count()


class Major(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "专业"
        ordering = ("school", "name")

    school = models.ForeignKey(School, verbose_name=School._meta.verbose_name, related_name="majors",
                               on_delete=models.PROTECT)
    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="school_majors", blank=True,
                              on_delete=models.PROTECT)
    name = models.CharField("名称", max_length=64, db_index=True)
    short_name = models.CharField("简称", max_length=64, blank=True, default="", db_index=True)
    college = models.ForeignKey("College", verbose_name="院系", related_name="majors", null=True, blank=True,
                                on_delete=models.PROTECT)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("修改时间", auto_now=True)
    study_years = models.PositiveSmallIntegerField("年制", blank=True, default=3)

    def __unicode__(self):
        return self.name


    def save(self, **kwargs):
        self.party = self.school.party
        self.short_name = self.short_name or self.name
        return super(Major, self).save(**kwargs)

    @property
    def student_count(self):
        return self.students.count()


class Clazz(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "班级"
        unique_together = ('school', 'entrance_session', 'grade', 'number')
        ordering = ('school', 'grade', 'number')

    school = models.ForeignKey(School, verbose_name=School._meta.verbose_name, related_name="clazzs",
                               on_delete=models.PROTECT)
    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="school_clazzs", blank=True,
                              on_delete=models.PROTECT)
    name = models.CharField("名称", max_length=64, db_index=True)
    number = models.CharField("编号", max_length=16, db_index=True)
    grade = models.ForeignKey(Grade, verbose_name=Grade._meta.verbose_name, related_name="clazzs")
    entrance_session = models.ForeignKey(Session, verbose_name="入学届别", related_name="entrance_clazzs")
    graduate_session = models.ForeignKey(Session, verbose_name="毕业届别", related_name="graduate_clazzs", null=True,
                                         blank=True)
    primary_teacher = models.ForeignKey(Teacher, verbose_name="班主任", related_name="clazzs", null=True,
                                        blank=True, on_delete=models.PROTECT)
    student_names = modelutils.WordSetField("学生名册", blank=True, help_text="学生姓名，一行一个", default=[])
    teacher_names = modelutils.KeyValueJsonField("老师名册", blank=True, default={},
                                                 help_text="""老师职责与老师姓名用':'隔开，一行一个, 如:<br/>
                                                 班主任:丁一成<br/>
                                                 语文:丁一成<br/>
                                                 数学:林娟""")
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    modify_time = models.DateTimeField("修改时间", auto_now=True)
    is_active = models.BooleanField("有效", default=True)

    def student_count(self):
        return len(self.student_names)

    student_count.short_description = '学生数'

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        self.party = self.school.party
        if not hasattr(self, 'entrance_session'):
            from . import helper
            self.entrance_session, created = helper.gen_default_session(self.school, self.grade.number - 1)
        return super(Clazz, self).save(**kwargs)


class Student(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "学生"

    school = models.ForeignKey(School, verbose_name=School._meta.verbose_name, related_name="students",
                               on_delete=models.PROTECT)
    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="school_students", blank=True,
                              on_delete=models.PROTECT)
    user = models.OneToOneField(User, verbose_name=User._meta.verbose_name, null=True, related_name="as_school_student",
                                on_delete=models.PROTECT)
    number = models.CharField("学号", max_length=32, db_index=True, null=True, blank=True)
    name = models.CharField("姓名", max_length=32, db_index=True)
    clazz = models.ForeignKey(Clazz, verbose_name=Clazz._meta.verbose_name, related_name="students", null=True,
                              blank=True,
                              on_delete=models.PROTECT)
    grade = models.ForeignKey(Grade, verbose_name=Grade._meta.verbose_name, related_name="students",
                              on_delete=models.PROTECT)
    entrance_session = models.ForeignKey(Session, verbose_name="入学届别", related_name="entrance_students",
                                         on_delete=models.PROTECT)
    graduate_session = models.ForeignKey(Session, verbose_name="毕业届别", related_name="graduate_students", null=True,
                                         blank=True, on_delete=models.PROTECT)

    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    modify_time = models.DateTimeField("修改时间", auto_now=True)
    is_active = models.BooleanField("有效", default=True)

    def __unicode__(self):
        return self.name

    def as_user(self):
        return self.user

    def save(self, **kwargs):
        self.party = self.school.party
        if not self.user:
            self.user = self.party.workers.create(name=self.name, position="学生").user
        # if not self.entrance_session:
        from . import helper
        y = helper.cur_grade_year(self.grade.number)
        self.entrance_session = self.school.sessions.get(number=y)
        return super(Student, self).save(**kwargs)
