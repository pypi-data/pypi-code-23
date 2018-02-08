


from django.core.cache import cache
from django.db import models


class CachingModelMixin:
    """
    Класс включается автоматически в цепочку наследования BaseAbstractModel, если CACHING=True
    Позволяет инвалидировать кеш в redis, при каждом сохранении объекта
    """

    @classmethod
    def get_map_key(cls):
        """
        Возвращет уникальный ключ для CACHE_MAP
        """
        return cls._meta.db_table

    def save(self, *args, **kwargs):
        """
        Удаляет все ключи в redis, в которых присутствует название вью из CACHE_MAP, по ключу данной модели
        """
        from .map import CACHE_MAP

        super().save(*args, **kwargs)
        key = self.__class__.get_map_key()
        views = CACHE_MAP.get(key)
        for view in views:
            cache.delete_pattern('*{}*'.format(view.get_cache_key()))

    class Meta:
        abstract = True
