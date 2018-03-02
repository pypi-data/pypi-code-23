import random
import datetime
import collections
import string
from django.utils.text import slugify


def parse_filename_to_args(name):
    """
    Parse filename and encode items for resolving in urls
    """
    name = name.lower()
    _prefix, app, model, field, _ = name.split('/')
    file_name, ext = _.split('.')
    return [app, model, field, file_name, ext]


def with_translate_options(default_cls, translate_cls, condition):
    """
    Принимает дефолтный класс админки, класс из библиотеки model-translate
    и поля из настроек OCTO_DRF, если есть какие то поля для перевода, возвращает model-traslate класс
    """
    from importlib import import_module

    if condition:
        translation = import_module('modeltranslation.admin')
        return getattr(translation, translate_cls)
    return default_cls


def redactor_fields_with_translate_options(*fields):
    """
    Принимает поля, в которых нужен редактор, возвращает эти поля с редактором
    и варианты этих полей со всеми языками из настройки LANGUAGES
    """
    from django.conf import settings
    from trumbowyg.widgets import TrumbowygWidget
    fields_dict = {i: TrumbowygWidget() for i in fields}
    

    if not settings.LANGUAGES:
        return fields_dict

    for field in fields:
        for lang in settings.LANGUAGES:
            code = lang[0].replace('-', '_')
            name = '{}_{}'.format(field, code)
            fields_dict[name] = TrumbowygWidget()
    return fields_dict


def increment_date(date=None, days=0, minutes=0, seconds=0):
    if not date:
        date = datetime.datetime.now()
    incremented = date + datetime.timedelta(days=days, minutes=minutes, seconds=seconds)
    return incremented

def get_namedtuple_choices(name, choices_tuple):
    """Factory function for quickly making a namedtuple suitable for use in a
    Django model as a choices attribute on a field. It will preserve order.

    Usage::

        class MyModel(models.Model):
            COLORS = get_namedtuple_choices('COLORS', (
                (0, 'BLACK', 'Black'),
                (1, 'WHITE', 'White'),
            ))
            colors = models.PositiveIntegerField(choices=COLORS.get_choices())

        > MyModel.COLORS.BLACK
        0
        > MyModel.COLORS.get_choices()
        [(0, 'Black'), (1, 'White')]

        class OtherModel(models.Model):
            GRADES = get_namedtuple_choices('GRADES', (
                ('FR', 'FR', 'Freshman'),
                ('SR', 'SR', 'Senior'),
            ))
            grade = models.CharField(max_length=2, choices=GRADES.get_choices())

        > OtherModel.GRADES.FR
        'FR'
        > OtherModel.GRADES.get_choices()
        [('FR', 'Freshman'), ('SR', 'Senior')]

    """
    class Choices(collections.namedtuple(name, [name for val, name, desc in choices_tuple])):
        __slots__ = ()
        _choices = tuple([desc for val, name, desc in choices_tuple])

        def get_choices(self):
            return zip(tuple(self), self._choices)

    return Choices._make([val for val, name, desc in choices_tuple])


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_key_generator(instance):
    """
    This is for a Django project with an key field
    """
    size = random.randint(30, 45)
    key = random_string_generator(size=size)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(key=key).exists()
    if qs_exists:
        return unique_slug_generator(instance)
    return key

def unique_slug_generator(instance, new_slug=None):
    """
    This is for a Django project and it assumes your instance 
    has a model with a slug field and a title character (char) field.
    """
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.title)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
                    slug=slug,
                    randstr=random_string_generator(size=4)
                )
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug
