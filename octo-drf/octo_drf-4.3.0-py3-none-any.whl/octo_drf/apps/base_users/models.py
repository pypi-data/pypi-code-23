from datetime import datetime

from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser


class BaseOctoUserManager(BaseUserManager):
    def create_user(self, email=None, password=None, **extra_fields):
        is_active = extra_fields.pop('is_active', True)
        now = datetime.now()
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_active=is_active,
            is_staff=False,
            is_superuser=False,
            date_joined=now,
            last_login=now,
            **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        u = self.create_user(email, password, **extra_fields)
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save(using=self._db)
        return u


class BaseOctoUser(AbstractBaseUser, PermissionsMixin):
    """"
    Абстрактная модель юзера
    """

    email = models.EmailField(
        verbose_name='Электронная почта',
        unique=True, )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=255,
        blank=True, )
    last_name = models.CharField(
        verbose_name=u'Фамилия',
        max_length=255,
        blank=True, )
    is_staff = models.BooleanField(
        verbose_name='Администратор сайта',
        default=False, )
    is_active = models.BooleanField(
        verbose_name='Активен',
        default=False, )
    date_joined = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True, )
    order = models.PositiveIntegerField(
        verbose_name='Порядок сортировки',
        default=10, )

    objects = BaseOctoUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        full_name = '{} {}'.format(self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    class Meta:
        abstract = True
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
