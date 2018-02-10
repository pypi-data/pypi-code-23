from django.db import models


class NUTS(models.Model):
    code = models.SlugField()
    name = models.CharField(max_length=250)
    level = models.PositiveSmallIntegerField()
    parent = models.ForeignKey('self', null=True)

    class Meta:
        ordering = ('code',)
        verbose_name = 'NUTS'
        verbose_name_plural = 'NUTS'

    def __str__(self):
        return self.name


class LAU(models.Model):
    nuts = models.ForeignKey(NUTS)
    code = models.SlugField()
    name = models.CharField(max_length=250)
    local_name = models.CharField(max_length=250)

    class Meta:
        ordering = ('code',)
        verbose_name = 'LAU'
        verbose_name_plural = 'LAU'

    def __str__(self):
        return self.name
