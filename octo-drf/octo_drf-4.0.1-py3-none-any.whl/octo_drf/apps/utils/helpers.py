


import datetime


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
    from redactor.widgets import RedactorEditor
    fields_dict = {i: RedactorEditor() for i in fields}

    if not settings.LANGUAGES:
        return fields_dict

    for field in fields:
        for lang in settings.LANGUAGES:
            code = lang[0].replace('-', '_')
            name = '{}_{}'.format(field, code)
            fields_dict[name] = RedactorEditor()
    return fields_dict


def increment_date(date=None, days=0, minutes=0, seconds=0):
    if not date:
        date = datetime.datetime.now()
    incremented = date + datetime.timedelta(days=days, minutes=minutes, seconds=seconds)
    return incremented
