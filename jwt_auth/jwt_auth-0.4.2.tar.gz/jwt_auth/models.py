# coding: utf-8
import uuid
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth.models import User, Group
from django.contrib.postgres.fields import JSONField
from functools import reduce


class StaffManager(BaseUserManager):

    def create_staff(self, email, password):
        if not email:
            raise ValueError('邮箱地址不能为空')
        if not password:
            raise ValueError('密码不合法.')

        staff = self.model(email=self.normalize_email(email), last_login=timezone.now())
        staff.set_password(password)
        staff.save(using=self._db)
        return staff


    def create_superuser(self, *args, **kwargs):
        staff = self.create_staff(*args, **kwargs)
        staff.is_admin = True
        staff.is_superuser = True
        staff.save(using=self._db)
        return staff


class Role(models.Model):
    name = models.CharField(u"名称", max_length=16, default="")

    def __str__(self):
        return self.name

    @property
    def menus(self):
        menus = self.permission_set.select_related('menu').only('menu').values_list('menu__menu_paths', flat=True)
        return reduce(lambda x, y: x + y, menus)

    # TODO: API有待详细设计
    def resources(self):
        pass

    class Meta:
        verbose_name_plural = verbose_name = u'角色'

class Menu(models.Model):
    name = models.CharField(u"名称", max_length=16, default="")
    menu_paths = JSONField(u'访问路径', default=list, help_text=u'选填', blank=False)
    is_active = models.BooleanField("是否激活", default=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = verbose_name = u'菜单'


class Resource(models.Model):
    name = models.CharField(u"名称", max_length=16, default="")
    api_path = models.CharField(u'API路径', max_length=200, help_text=u'选填', default='')
    is_active = models.BooleanField("是否激活", default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = verbose_name = u'资源'


class Staff(AbstractBaseUser):
    username = models.CharField(u"用户名", max_length=24, default="")
    email = models.EmailField(u"邮件", max_length=255, unique=True, db_index=True)
    is_active = models.BooleanField("是否激活", default=True)
    is_admin = models.BooleanField("是否管理员", default=False)
    introduce_by = models.CharField(u"推荐由", max_length=64, default="")
    date_joined = models.DateTimeField(u'创建时间', auto_now=True)
    roles = models.ManyToManyField(Role, verbose_name=u'角色', blank=True)
    objects = StaffManager()

    USERNAME_FIELD = 'email'

    @property
    def is_staff(self):
        return self.is_active

    def __str__(self):
        return self.email

    @property
    def menus(self):
        roles = self.roles.prefetch_related('permission_set')
        menus = [m.menus for m in roles]
        if not menus:
            return []
        return list(set(reduce(lambda x, y: x + y, menus)))

    def has_module_perms(self, demo):
        return True


    def has_perm(self, perm, obj=None):
        return True

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])

    def get_short_name(self):
        # The user is identified by their email address
        return self.email


    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def fake_username(self):
        return self.email.split('@')[0]

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True

    class Meta:
        verbose_name_plural = verbose_name = u'活动用户'


class Permission(models.Model):
    name = models.CharField(u"名称", max_length=24, default="")
    menu = models.OneToOneField(Menu, verbose_name=u'菜单组', 
                related_name='permissions', on_delete=models.SET_NULL, null=True)
    resources = models.ManyToManyField(Resource, verbose_name=u'资源',
        blank=True)
    roles = models.ManyToManyField(Role, verbose_name=u'角色',
        blank=True)
    is_active = models.BooleanField("是否激活", default=True)

    def __str__(self):
        return self.name


    class Meta:
        verbose_name_plural = verbose_name = u'权限'


