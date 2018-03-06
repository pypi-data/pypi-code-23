#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'zhangyue'



# Create your models here.
import os
from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings
from smart_selects.db_fields import ChainedForeignKey
from django.core.files.storage import FileSystemStorage


# 性别
PREUSER_GENDER_CHOICES = ((1, '男'), (2, '女'))
# 意向
PREUSER_GRADE_CHOICES = ((0, '无'), (1, '弱'), (2, '强'))
# 申请表的问题类型
APPLICATION_QUESTION_INPUT_TYPE_CHOICES = ((1, '输入框'), (2, '单选（圆钮）'), (3, '单选（下拉）'), (4, "多选（方钮）"))
# 级别
PREUSER_LEVEL_CHOICES = ((0, '全部'), (1, '小白'), (2, '申请'), (3, '缴费'))
# 合同周期
CONTRACT_PERIOD_CHOICES = ((7, '周'), (30, '月'))


def get_user_table():
    if settings.CRM_USER_TABLE in ["", None]:
        user_table = User
    else:
        user_table = settings.CRM_USER_TABLE
    return user_table


def get_user_name_field():
    return settings.CRM_USER_NAME_FIELD


# 省市区联动
class Province(models.Model):
    name = models.CharField(max_length=180, null=True)

    class Meta:
        db_table = 'bee_django_crm_province'
        app_label = 'bee_django_crm'

    def __unicode__(self):
        return self.name


class City(models.Model):
    province = models.ForeignKey(Province)
    name = models.CharField(max_length=180, null=True)

    class Meta:
        db_table = 'bee_django_crm_city'
        app_label = 'bee_django_crm'

    def __unicode__(self):
        return self.name


class District(models.Model):
    city = models.ForeignKey(City)
    # city=ChainedForeignKey(City,chained_field='continent',show_all=False,auto_choose=True,sort=True)
    name = models.CharField(max_length=180, null=True)

    class Meta:
        db_table = 'bee_django_crm_district'
        app_label = 'bee_django_crm'

    def __unicode__(self):
        return self.name


# 预备学员
class PreUser(models.Model):
    nickname = models.CharField(verbose_name='昵称', max_length=180, null=True, blank=True)  # 昵称
    name = models.CharField(verbose_name='姓名', max_length=20)  # 姓名
    mobile = models.CharField(verbose_name='电话', max_length=15, unique=True)  # 手机
    gender = models.IntegerField(verbose_name='性别', null=True, blank=True, default=0)  # 性别
    wx = models.CharField(verbose_name='微信', max_length=180, null=True, blank=True)  # 微信
    birthday = models.DateField(verbose_name='出生日期', null=True, blank=True)
    province = models.ForeignKey(Province, null=True, blank=True, verbose_name='省')
    city = ChainedForeignKey(
        City,
        chained_field="province",
        chained_model_field="province",
        show_all=False,
        auto_choose=True,
        sort=True,
        null=True,
        blank=True,
        verbose_name='市')
    source = models.ForeignKey("bee_django_crm.Source", verbose_name='来源', null=True, blank=True)  # 来源
    referral_user = models.ForeignKey(get_user_table(), related_name='bee_crm_referral_user', null=True, blank=True,
                                      verbose_name='转介人')  # 转介人
    level = models.IntegerField(verbose_name='级别', default=1)  # 级别 1-小白，2-已申请 3-已缴费
    grade = models.IntegerField(verbose_name='意向', null=True, blank=True)  # 意向 1-弱 2-强

    address = models.TextField(verbose_name='地址', null=True, blank=True)

    job = models.CharField(verbose_name='工作', max_length=180, null=True, blank=True)
    email = models.CharField(verbose_name='邮箱', max_length=180, null=True, blank=True)
    hobby = models.TextField(verbose_name='爱好', null=True, blank=True)
    married = models.CharField(verbose_name='婚姻状况', max_length=180, null=True, blank=True)  # 婚否
    children = models.CharField(verbose_name='孩子状况', max_length=180, null=True, blank=True)  # 有几个孩子
    job_info = models.TextField(verbose_name='工作详情', null=True, blank=True)  # 工作详情
    family = models.TextField(verbose_name='家庭详情', null=True, blank=True)  # 家庭情况
    # 缴费记录
    contract_id = models.IntegerField(verbose_name='合同', null=True, blank=True)
    fee = models.FloatField(verbose_name='缴费金额', null=True, blank=True)
    info = models.TextField(verbose_name='备注', null=True, blank=True)
    is_add_coin = models.IntegerField(verbose_name='加缦币', default=0, null=True, blank=True)  # 0-未加缦币，1-已加缦币
    attended_date = models.DateField(verbose_name='入学日期', null=True, blank=True)  # 入学日期
    pay_datetime = models.DateField(verbose_name='缴费日期', null=True, blank=True)  # 缴费日期
    # coupon = models.ForeignKey("other.Coupon", related_name='bee_crm_preUser_coupon', null=True)  # 注册时使用的课程卡
    #
    created_at = models.DateTimeField(auto_now_add=True, null=True)  # 注册时间
    applied_at = models.DateTimeField(null=True)  # 提交申请表时间
    paid_at = models.DateTimeField(null=True)  # 缴费时间

    class Meta:
        db_table = 'bee_django_crm_preuser'
        app_label = 'bee_django_crm'
        ordering = ["-created_at"]

    def get_absolute_url(self):
        return reverse('bee_django_crm:preuser_detail', kwargs={'pk': self.pk})

    def get_gender(self):
        if not self.gender:
            return ""
        for g in PREUSER_GENDER_CHOICES:
            if self.gender == g[0]:
                return g[1]
        return ""

    def get_grade(self):
        if not self.grade:
            return ""
        for g in PREUSER_GRADE_CHOICES:
            if self.grade == g[0]:
                return g[1]
        return ""

    def get_source(self):
        if not self.source:
            return ""
        return self.source.name

    def get_level(self):
        if not self.level:
            return ""
        for g in PREUSER_LEVEL_CHOICES:
            if self.level == g[0]:
                return g[1]
        return ""

    def __unicode__(self):
        return ("PreUser->name:" + self.name)


# 来源
class Source(models.Model):
    name = models.CharField(max_length=60, verbose_name="来源名称")  # 名称
    reg_name = models.CharField(max_length=60, verbose_name="注册页显示名称", null=True, blank=True)  # 注册页显示名称
    created_at = models.DateTimeField(auto_now_add=True)  # 时间
    is_poster = models.BooleanField(default=False, verbose_name='是否海报类型', blank=True)
    is_show = models.BooleanField(default=False, verbose_name='编辑时是否显示', blank=True)

    class Meta:
        db_table = 'bee_django_crm_source'
        app_label = 'bee_django_crm'
        ordering = ['-created_at']

    def __unicode__(self):
        return (self.name)

    def get_absolute_url(self):
        return reverse('bee_django_crm:source_list')

    def get_is_poster(self):
        if self.is_poster == True:
            return "是"
        elif self.is_poster == False:
            return "否"

    def get_show_posters(self):
        return self.poster_set.filter(is_show=True)


# 联络记录
class PreUserTrack(models.Model):
    user = models.ForeignKey("bee_django_crm.PreUser", related_name='bee_crm_track_user')  # 追踪人
    created_at = models.DateTimeField(auto_now_add=True)  # 记录时间
    tracked_at = models.DateTimeField(verbose_name='联络时间')  # 追踪时间
    info = models.TextField(verbose_name="详情")  # 详情
    created_by = models.ForeignKey(get_user_table(), null=True, related_name='bee_crm_created_by_user')  # 操作人

    class Meta:
        db_table = 'bee_django_crm_preuser_track'
        app_label = 'bee_django_crm'

    def __unicode__(self):
        return ("PerUserTrack->info:" + self.user.name)

    def get_absolute_url(self):
        return reverse('bee_django_crm:preuser_detail', kwargs={'pk': self.user.pk})


# 申请表问题
class ApplicationQuestion(models.Model):
    name = models.CharField(max_length=180, unique=True, verbose_name='问题')  # 问题
    order_by = models.IntegerField(verbose_name='顺序')  # 顺序
    input_type = models.IntegerField(choices=APPLICATION_QUESTION_INPUT_TYPE_CHOICES, verbose_name='类型')  # 类型

    class Meta:
        db_table = 'bee_django_crm_application_question'
        app_label = 'bee_django_crm'
        ordering = ["order_by"]

    def __unicode__(self):
        return ("ApplicationQuestion->question:" + self.name)

    def get_absolute_url(self):
        return reverse('bee_django_crm:application_question_list')

    def get_type_name(self):
        if not self.input_type:
            return ""
        for g in APPLICATION_QUESTION_INPUT_TYPE_CHOICES:
            if self.input_type == g[0]:
                return g[1]
        return ""


# 申请表问题的选项
class ApplicationOption(models.Model):
    question = models.ForeignKey('bee_django_crm.ApplicationQuestion', verbose_name='问题')
    name = models.CharField(verbose_name='选项', max_length=180, unique=True)
    order_by = models.IntegerField(verbose_name='顺序')

    class Meta:
        db_table = 'bee_django_crm_application_options'
        app_label = 'bee_django_crm'
        ordering = ["order_by"]

    def __unicode__(self):
        return ("ApplicationOption->option:" + self.name)


# 学生填的申请表内容
class PreUserApplication(models.Model):
    preuser = models.ForeignKey('bee_django_crm.PreUser', related_name='bee_crm_user_applications')
    question = models.ForeignKey('bee_django_crm.ApplicationQuestion')
    answer = models.TextField()

    class Meta:
        db_table = 'bee_django_crm_preuser_application'
        app_label = 'bee_django_crm'

    def __unicode__(self):
        return ("PreUserApplication->preuser:" + self.preuser.name)


# 合同
class Contract(models.Model):
    name = models.CharField(verbose_name='合同名称', max_length=180, unique=True)  # 合同名称
    period = models.IntegerField(verbose_name='周期')  # 月／周
    duration = models.IntegerField(verbose_name='时长')  # 时长
    price = models.FloatField(verbose_name='金额')  # 金额

    class Meta:
        db_table = 'bee_django_crm_contract'
        app_label = 'bee_django_crm'
        ordering = ["-id"]

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('bee_django_crm:contract_list')


# 用户的合同表
class PreUserContract(models.Model):
    preuser = models.ForeignKey('bee_django_crm.PreUser')
    contract = models.ForeignKey('bee_django_crm.Contract', verbose_name='合同')
    price = models.FloatField(verbose_name='实收金额')  # 金额
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(verbose_name='缴费日期')
    study_at = models.DateTimeField(verbose_name='开课日期', null=True, blank=True)
    info = models.TextField(null=True, blank=True, verbose_name='备注')
    is_checked = models.BooleanField(verbose_name='审核', default=False, blank=True)
    checked_at = models.DateTimeField(null=True)
    checked_by = models.ForeignKey(get_user_table(), null=True)
    # is_after_check = models.IntegerField(default=False,null=True)
    after_checked_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'bee_django_crm_preuser_contract'
        app_label = 'bee_django_crm'
        ordering = ['-paid_at']

    def __unicode__(self):
        return ("PreUserContract->name:" + self.preuser.name)


# 海报
POSTER_SHOW_CHOICES = ((1, '显示'), (0, '不显示'))
fs = FileSystemStorage(location=settings.CRM_POSTER_PHOTO_PATH)


class Poster(models.Model):
    source = models.ForeignKey('bee_django_crm.Source')
    # name = models.CharField(max_length=180, verbose_name='海报名称')
    is_show = models.BooleanField(default=False, verbose_name='是否显示', blank=True)
    # is_clear = models.BooleanField(default=False, verbose_name='是否清空文件', blank=True)
    qrcode_width = models.IntegerField(verbose_name='二维码宽度', null=True, default=0)
    qrcode_height = models.IntegerField(verbose_name='二维码高度', null=True, default=0)
    qrcode_pos_x = models.IntegerField(verbose_name='二维码x轴坐标', null=True, default=0)
    qrcode_pos_y = models.IntegerField(verbose_name='二维码y轴坐标', null=True, default=0)
    qrcode_color = models.CharField(max_length=8, verbose_name='二维码颜色', default='#000000', null=True)
    photo = models.ImageField(storage=fs, null=True)

    class Meta:
        db_table = 'bee_django_crm_poster'
        app_label = 'bee_django_crm'

    def __unicode__(self):
        return self.source.name

    def get_temp_image(self):
        return os.path.join(settings.CRM_POSTER_PHOTO_PATH, self.id.__str__() + '_temp.jpg')

    def get_image_count(self):
        image_dir = os.path.join(settings.CRM_POSTER_PHOTO_PATH, self.id.__str__())
        if not os.path.exists(image_dir):
            return 0
        return len([name for name in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, name))])

    def get_is_show(self):
        if self.is_show == True:
            return "是"
        elif self.is_show == False:
            return "否"
