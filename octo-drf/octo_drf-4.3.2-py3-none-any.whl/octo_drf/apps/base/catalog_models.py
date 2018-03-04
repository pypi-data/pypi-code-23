from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from mptt.managers import TreeManager
from mptt.models import MPTTModel

from octo_drf.apps.generic_image.fields import SorlImageField

from .models import BaseAbstractModel, BaseManager


class BaseAbstractCatalog(BaseAbstractModel):
    """
    Базовая модель каталога с generic ссылками на Галерею, Блоки и Виджеты
    """
    gallery = GenericRelation(
        'gallery.Gallery',
        verbose_name='Галерея',
        related_name='gallery'
    )
    static_blocks = GenericRelation(
        'static_blocks.StaticBlock',
        verbose_name='Блоки',
        related_name='static_blocks'
    )
    widgets = GenericRelation(
        'widgets.Widget',
        verbose_name='Виджеты',
        related_name='widgets'
    )
    slug = models.SlugField(
        'URL страницы',
        unique=True
    )

    class Meta:
        abstract = True


class AbstractCatalog(BaseAbstractCatalog):
    """
    Модель каталога с расширенными полями
    """
    title = models.CharField(
        'Заголовок',
        max_length=255,
        blank=True
    )
    note = models.TextField(
        'Краткое описание',
        blank=True
    )
    content = models.TextField(
        'Описание страницы',
        blank=True
    )
    image = SorlImageField(
        'Изображение',
        lookup_name='image',
        blank=True
    )

    class Meta:
        abstract = True


class AbstractCategory(AbstractCatalog):

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class AbstractItem(AbstractCatalog):

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        verbose_name = 'Item'
        verbose_name_plural = 'Items'


class MPTTManager(TreeManager, BaseManager):

    def get_queryset(self, exclude_no_published=True, *args, **kwargs):
        """
        Метод перегружен для поддержки всех возможностей TreeManager
        """

        return super().get_queryset(
            *args, **kwargs
        ).order_by(
            self.tree_id_attr, self.left_attr
        )


class MPTTActionMixin:

    @classmethod
    def _get_model_fields(cls):
        mptt_fields = ['lft', 'rght', 'tree_id', 'level']
        fields = super(MPTTActionMixin, cls)._get_model_fields()
        fields = [i for i in fields if i not in mptt_fields]
        return fields

    @classmethod
    def get_serializer_fields(cls, *additional_fields):
        fields = super(MPTTActionMixin, cls).get_serializer_fields(*additional_fields)
        fields.append('ancestors')
        return fields

    @property
    def ancestors(self):
        ancestors = self.get_ancestors()
        return [{'id': i.pk, 'name': i.name, 'slug': i.slug} for i in ancestors]


class MPTTCategory(MPTTModel, MPTTActionMixin, AbstractCategory):
    """
    Абстрактная модель древовидной категории с расширенным полями
    """
    parent = models.ForeignKey(
        'self',
        verbose_name='Родительская категория',
        related_name='children',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )

    all_objects = TreeManager()
    objects = MPTTManager()

    class Meta:
        abstract = True


class SimpleMPTTCategory(MPTTModel, MPTTActionMixin, BaseAbstractCatalog):
    """
    Абстрактная модель древовидной категории
    """
    parent = models.ForeignKey(
        'self',
        verbose_name='Родительская категория',
        related_name='children',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )

    all_objects = TreeManager()
    objects = MPTTManager()

    class Meta:
        abstract = True
