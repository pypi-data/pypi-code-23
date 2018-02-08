


from django.apps import apps
from django.http import Http404
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404

from octo_drf.apps.utils.exceptions import DBInfoException

registered_forms = []  # Список для регистрации форм


def get_view_name(cls):
    name = cls.__name__
    if name.rfind('View') > 0:
        return name[:name.rfind('View')].lower()
    return name.lower()


def register_form(func):
    """
    Декоратор для регистрации форм
    """
    name = get_view_name(func)
    registered_forms.append(name)
    return func


class InstanceFromDBInfoMixin:
    """
    Миксин для работы с уникальным идентификатором модели.
    Позволяет получать модель по идентификатору из request.data или request.query_params
    """

    def _restore_instance_from_request(self):
        string_data = self.request.query_params.get('db_info')
        if string_data:
            data = string_data.split(',')
        else:
            data = self.request.data.get('db_info')
        if not data:
            return

        for i, v in enumerate(data):
            data[i] = v.strip()
        return data

    def restore_model_instance(self, db_info=None):
        """
        Возвращает модель из поля db_info, обращаясь к request.query_params и request.data
        Так же принимает db_info, если нужно передать идентификатор модели вручную, ввиде одной строки
        """
        if db_info:
            data = db_info.split(',')
        else:
            data = self._restore_instance_from_request()
        try:
            app, model, pk = data
        except (ValueError, TypeError):
            raise DBInfoException('db_info должен представлять список "app_name, model_name, model_id"')
        model_from_info = apps.get_model(app, model)
        instance = get_object_or_404(model_from_info.objects.all(), pk=pk)
        return instance

    def restore_multiply_instances(self):
        """
        Формирует словарь из GET параметров, вида {query_params_key: instance }
        """
        query_params = self.request.query_params
        instances = {}
        for k in query_params:
            try:
                instances[k] = self.restore_model_instance(query_params[k])
            except Http404:
                instances[k] = None
        return instances


class BaseModelViewSet(InstanceFromDBInfoMixin, viewsets.ModelViewSet):
    """
    Базовый ModelViewSet
    """


class BaseReadOnlyModelViewSet(InstanceFromDBInfoMixin, viewsets.ReadOnlyModelViewSet):
    """
    Базовый ReadOnlyModelViewSet, добавляет поддержку кеша
    """
