from django.db import models


class BaseQueryset(models.QuerySet):
    def with_gallery_and_static_counts(self):
        qs = self.annotate(count_static_block=models.Count('static_block', distinct=True)).annotate(count_gallery=models.Count('gallery', distinct=True))
        return qs


class BaseManager(models.Manager):
    """
    Дефолтный менеджер, исключает все объекты с полем is_published=False
    """
    queryset_class = BaseQueryset
    use_for_related_fields = True

    def get_queryset(self, exclude_no_published=True):
        q = self.queryset_class(self.model)
        q = q.exclude(is_published=False)
        return q

    def with_gallery_and_static_counts(self):
        return self.get_queryset().with_gallery_and_static_counts()


class DynamicModelFieldsMixin:
    """
    Миксин позволяет динамически определять поля для сериалайзера и адмнини
    Добавляет поддержку автоматического создания филдсетов в админке и полей в сериалазере,
    при условии наследования от BaseAdmin и BaseModelSerializer
    excluded_fields = []             Поля которые нужно исключить и в сериалайзере и в админке
    excluded_admin_fields = []       Поля которые нужно исключить только в админке
    excluded_serializer_fields = []  Поля которые нужно исключить только в сериалайзере
    """
    excluded_fields = []
    excluded_admin_fields = []
    excluded_serializer_fields = []

    @classmethod
    def _get_model_fields(cls):
        """
        Вернуть все поля модели, за исключением вспомогательных полей-ссылок
        """
        all_fields = cls._meta.get_fields()
        fields = [i.name for i in all_fields if i.__class__.__name__ not in [
            'ManyToManyRel', 'GenericRelation', 'ManyToOneRel', 'GenericForeignKey']]
        return fields

    @classmethod
    def _build_admin_fields(cls, fields):
        """
        Возвращает список полей для админа, отфилтрованных через excluded_* списки
        """
        modified_fields = [
            i for i in fields
            if i not in cls.excluded_fields and i not in cls.excluded_admin_fields
        ]
        return modified_fields

    @classmethod
    def _build_serializer_fields(cls, fields):
        """
        Возвращает список полей для сериалайзера, отфилтрованных через excluded_* списки
        Добавляет поле с идентификатором модели
        """
        modified_fields = [
            i for i in fields
            if i not in cls.excluded_fields and i not in cls.excluded_serializer_fields
        ]
        return modified_fields

    @classmethod
    def get_serializer_fields(cls, *additional_fields):
        """
        Возвращает поля для сериалайзера, расширяется произвольным набором полей
        """
        fields = cls._get_model_fields()
        fields.extend(additional_fields)
        return cls._build_serializer_fields(fields)

    @classmethod
    def get_admin_fields(cls):
        """
        Вовзращает поля для админки
        """
        fields = cls._get_model_fields()
        return cls._build_admin_fields(fields)


class BaseAbstractModel(DynamicModelFieldsMixin, models.Model):
    """
    Базовый класс для наследования всех моделей.
    """
    name = models.CharField(
        'Название',
        max_length=255
    )
    is_published = models.BooleanField(
        'Опубликовано',
        default=True
    )
    order = models.PositiveIntegerField(
        'Порядок сортировки',
        default=10,
    )

    # all_objects - дефолтный менеджер для модели, нужен для корректной работы некоторых частей Django
    # таких как list_page в админке, например
    all_objects = models.Manager()
    objects = BaseManager()

    def __str__(self):
        return self.name

    class Meta:
        abstract = True

