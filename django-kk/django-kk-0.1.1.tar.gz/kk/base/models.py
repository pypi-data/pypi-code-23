from django.db import models

class Base(models.Model):
    created_date = models.DateTimeField(
        auto_now_add = True
    )

    modified_date = models.DateTimeField(
        auto_now = True
    )

    status = models.BooleanField(
        'Опубликовано',
        default = True
    )

    class Meta:
        abstract = True


class OrderedMixin(models.Model):
    position = models.PositiveSmallIntegerField(
        'Позиция',
        null = True,
        blank = True
    )

    def unordered(self):
        return self.position == None

    class Meta:
        abstract = True


class Ordered(OrderedMixin, Base):
    class Meta:
        abstract = True


class XMLCodeMixin(models.Model):
    xml = models.TextField(
        'Код',
        blank = True
    )

    class Meta:
        abstract = True
