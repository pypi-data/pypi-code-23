from django.db import models

from octo_drf.apps.base.models import DynamicModelFieldsMixin
from octo_drf.apps.generic_image.fields import SorlImageField
from octo_drf.apps.mailer.api import notify_user, notify_admin


class FormMeta(DynamicModelFieldsMixin, models.Model):
    """
    Модель хранит в себе мета данные каждой формы
    """

    form_name = models.CharField(
        'Название формы',
        max_length=255,
        unique=True
    )
    title = models.CharField(
        'Заголовок',
        max_length=500,
        blank=True
    )
    description = models.TextField(
        'Описание',
        blank=True
    )
    button = models.CharField(
        'Текст для кнопки',
        max_length=500,
        blank=True
    )
    error_message = models.TextField(
        'Сообщение при ошибке',
        blank=True
    )
    success_message = models.TextField(
        'Сообщение при успехе',
        blank=True
    )
    error_button = models.CharField(
        'Кнопка для ошибки',
        max_length=500,
        blank=True
    )
    success_image = SorlImageField(
        'Изображение для успешного ответа',
        lookup_name='success_image',
        blank=True
    )
    url = models.CharField(
        'URL формы',
        max_length=500,
        blank=True
    )
    require = models.CharField(
        'Ошибка: Обязательное поле',
        max_length=500,
        blank=True
    )
    pattern = models.CharField(
        'Ошибка: Соответствие формату',
        max_length=500,
        blank=True
    )

    def __str__(self):
        return self.form_name

    class Meta:
        verbose_name = 'Мета данные формы'
        verbose_name_plural = 'Мета данные форм'


class FormFieldMeta(DynamicModelFieldsMixin, models.Model):
    """
    Модель хранит в себе мета данные полей для моделей форм
    """

    form_meta = models.ForeignKey(
        FormMeta,
        verbose_name='Мета данные формы',
        related_name='fields_meta',
        on_delete=models.CASCADE
    )
    field_name = models.CharField(
        'Название поля',
        max_length=100
    )
    title = models.CharField(
        'Заголовок',
        max_length=255,
        blank=True
    )
    placeholder = models.CharField(
        'Плейсхолдер',
        max_length=255,
        blank=True
    )
    image = SorlImageField(
        'Иконка',
        lookup_name='image',
        blank=True
    )
    error_message = models.TextField(
        'Сообщение при ошибке',
        blank=True
    )

    def __str__(self):
        return self.field_name

    class Meta:
        unique_together = ('form_meta', 'field_name')
        verbose_name = 'Мета данные поля формы'
        verbose_name_plural = 'Мета данные полей форм'


class AbstractBaseForm(DynamicModelFieldsMixin, models.Model):
    """
    Базовая модель форм, стандартная Django модель.
    Все перечесленные поля модели, после заполнения формы отправляются в контекст шаблона,
    при сохранении в стандартном сериалазейре форм

    атрибут template_name определяет шаблон использующийся для формы.
    Шаблон определяется по полю template_name модели UserTemplate.
    Если template_name не задан то используется щаблон с именем модели формы.
    При его остуствии он будет создан моделью шаблона
    """
    excluded_fields = ['id']

    to_email = models.EmailField(
        'Почта пользователя',
        blank=True
    )
    page_url = models.CharField(
        'Адрес с которого отправлена форма',
        max_length=255
    )
    date_add = models.DateField(
        'Дата добавления',
        auto_now_add=True
    )

    def send_form_mail(self, context=None):
        context = self._update_context(context)
        template_name = self._meta.model_name
        if self.to_email:
            notify_user(template_name, self.to_email, context=context)
        else:
            notify_admin(template_name, context=context)

    def _update_context(self, context):
        form_data = {'id': self.pk}
        if context:
            context.update(form_data)
        else:
            context = form_data
        return context

    class Meta:
        abstract = True
