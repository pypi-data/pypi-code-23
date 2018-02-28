import requests
import os

from django.db import models
from django.db.models import Q
from django.template import TemplateDoesNotExist
from django.template.loader import get_template, render_to_string
from django.conf import settings


TEMPLATE_INFO = """
    Title: {{ title }}
    Content: {{ content }}
    Footer: {{ footer }}
"""
DEFAULT_FROM = settings.MAIL_FROM
DEFAULT_SUBJECT = settings.MAIL_SUBJECT


class BaseMailTemplate(models.Model):
    """
    Базовая модель шаблона, содержит основные поля необходимые для вывода в шаблон письма,
    все поля кроме name и template не обязательны
    Основная идея модели - позволить редактировать html шаблоны писем из админки, заполняя поля title, content, footer
    """
    template_prefix = ''

    name = models.SlugField(
        'Название шаблона',
        max_length=255,
        unique=True
    )
    template = models.CharField(
        'HTML шаблон',
        help_text='Название HTML шаблона. Создается автоматически, на основе имени '
                  'Если одноименного шаблона нету в папке, он будет создан автомачески',
        max_length=255,
        editable=False,
    )
    subject = models.CharField(
        'Тема письма',
        max_length=255,
        default=DEFAULT_SUBJECT,
    )
    from_email = models.CharField(
        'От кого письмо',
        max_length=255,
        default=DEFAULT_FROM,
    )
    title = models.CharField(
        'Заголовок',
        max_length=255,
        blank=True
    )
    content = models.TextField(
        'Контент',
        blank=True
    )
    footer = models.TextField(
        'Футер',
        blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True

    def get_context(self):
        return {
            'title': self.title,
            'content': self.content,
            'footer': self.footer
        }

    def save(self, *args, **kwargs):
        template_name = 'mail_templates/{}_{}.html'.format(self.template_prefix, self.name)
        try:
            self.template = get_template(template_name).template.name
        except TemplateDoesNotExist:
            path = os.path.join(settings.BASE_DIR, 'templates/{}'.format(template_name))
            with open(path, 'w') as f:
                f.write(TEMPLATE_INFO)
            self.template = template_name
        return super().save(*args, **kwargs)


class AdminTemplate(BaseMailTemplate):
    """
    Шаблон писем для отправки администраторам сайта,
    в admin_url указывается урл админки, который нужно прикреплять к письму
    subscribers - m2m связь с администраторами сайта,
    должен быть хотя бы один подписчик, который будет получать уведомления при заполнении формы
    """
    template_prefix = 'admin'

    subscribers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name='Подписчики',
        related_name='mail_forms',
        limit_choices_to=Q(is_staff=True) | Q(is_superuser=True)
    )
    admin_url = models.CharField(
        'URL страницы в админке',
        max_length=500,
        blank=True
    )

    class Meta:
        verbose_name = 'Шаблон для админа'
        verbose_name_plural = 'Шаблоны для админа'

    def get_subs_emails(self):
        return [i.email for i in self.subscribers.all()]

    def get_context(self):
        context = super().get_context()
        if self.admin_url:
            context.update({'admin_url': self.admin_url})
        return context


class UserTemplate(BaseMailTemplate):
    """
    Шаблон писем для отправки пользователям,
    admin_template не обязательная связь между шаблоном админа, если связь указана, админ будет получать уведомления,
    каждый раз когда заполняется форма юзера
    """
    template_prefix = 'user'

    admin_template = models.OneToOneField(
        AdminTemplate,
        verbose_name='Шаблон для администратора',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Шаблон для пользователя'
        verbose_name_plural = 'Шаблоны для пользователя'


class AbstractNotifier:
    """
    Абстрактный класс для отправки писем с html контентом, с помощью моделей шаблонов
    """
    def __init__(self, template, from_email=None, subject=None, context=None):
        self._template = template
        self.from_email = from_email
        self.subject = subject
        self.context = context if context else {}

    @staticmethod
    def send_message_via_api(text, to_email, from_email, subject):
        return requests.post(
            settings.API_MESSAGES,
            auth=('api', settings.API_KEY),
            data={
                'text': text,
                'to': to_email,
                'from': from_email,
                'subject': subject
            }
        )

    def _render_template(self, template):
        context_dict = template.get_context()
        context_dict.update(self.context)
        return render_to_string(template.template, context_dict)

    def _send_mail(self, template, to_email, from_email, subject):
        return requests.post(
            settings.API_MESSAGES,
            auth=('api', settings.API_KEY),
            data={
                'html': template,
                'to': to_email,
                'from': from_email,
                'subject': subject,
            }
        )


class AdminNotifier(AbstractNotifier):
    """
    Класс для отправки оповещений админам, через шаблоны администратора.
    Не принимает to_email, т.к. использует подписчиков (m2m связь с админами, в модели шаблона)
    """

    def __init__(self, template, **kwargs):
        super().__init__(template, **kwargs)

    @property
    def template(self):
        template, _ = AdminTemplate.objects.get_or_create(name=self._template)
        return template

    def notify_subs(self):
        subs = self.template.get_subs_emails()
        rendered_template = self._render_template(self.template)
        from_email = self.from_email if self.from_email else self.template.from_email
        subject = self.subject if self.subject else self.template.subject
        return self._send_mail(
                rendered_template,
                subs,
                from_email,
                subject
            )


class UserNotifier(AbstractNotifier):
    """
    Класс для отправки оповещения пользователю, используя шаблоны для пользователя
    Если у шаблона есть связь с шаблоном админа то при отправке, так же отправит оповещения всем подписчикам шаблона админа
    """

    def __init__(self, template, to_email, **kwargs):
        self.to_email = to_email
        super().__init__(template, **kwargs)

    @property
    def template(self):
        template, _ = UserTemplate.objects.get_or_create(name=self._template)
        return template

    def notify_user(self):
        self.notify_admin()

        rendered_template = self._render_template(self.template)
        from_email = self.from_email if self.from_email else self.template.from_email
        subject = self.subject if self.subject else self.template.subject
        return self._send_mail(
                rendered_template,
                self.to_email,
                from_email,
                subject
            )

    def notify_admin(self):
        admin_template = self.template.admin_template
        if admin_template:
            notifier = AdminNotifier(admin_template.name,
                                     from_email=self.from_email,
                                     subject=self.subject,
                                     context=self.context
                                     )
            return notifier.notify_subs()
