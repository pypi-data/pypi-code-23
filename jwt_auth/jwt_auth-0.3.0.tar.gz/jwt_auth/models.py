# coding: utf-8
import uuid
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils import timezone


class StaffManager(BaseUserManager):

    def create_staff(self, email, password, **kwargs):
        if not email:
            raise '邮箱地址不能为空'
        if not password:
            raise ValueError('密码不合法.')
        if not password == kwargs.get('confirm_password'):
            raise ValueError('请确认你的密码.')

        staff = self.model(email=self.normalize_email(email), last_login=timezone.now())
        staff.set_password(password)
        staff.save(using=self._db)
        return staff


    def create_superuser(self, email, password):
        staff = self.create_staff(email, password)
        staff.is_admin = True
        staff.save(using=self._db)
        return staff


class Staff(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(u"用户名", max_length=24, default="")
    email = models.EmailField(u"邮件", max_length=255, unique=True, db_index=True)
    is_active = models.BooleanField("是否激活", default=True)
    is_admin = models.BooleanField(default=False)
    introduce_by = models.CharField(u"推荐由", max_length=64, default="")
    date_joined = models.DateTimeField(u'创建时间', auto_now=True)

    objects = StaffManager()

    USERNAME_FIELD = 'email'

    def is_staff(self):
        return not self.is_admin

    def __str__(self):
        return self.email


    def has_module_perms(self, demo):
        return True


    def has_perm(self, perm, obj=None):
        return True


    def get_short_name(self):
        # The user is identified by their email address
        return self.email


    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def fake_username(self):
        return self.email.split('@')[0]
