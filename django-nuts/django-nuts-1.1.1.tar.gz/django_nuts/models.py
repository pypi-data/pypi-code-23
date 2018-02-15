from django.db import models
from django.utils.functional import cached_property


class NUTS(models.Model):
    code = models.CharField(max_length=6, primary_key=True)
    name = models.CharField(max_length=250)
    level = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ('code',)
        verbose_name = 'NUTS'
        verbose_name_plural = 'NUTS'

    def __str__(self):
        return self.name

    @cached_property
    def laus(self):
        return LAU.objects.filter(nuts__code__startswith=self.code)


class LAU(models.Model):
    code = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=250)
    local_name = models.CharField(max_length=250)
    nuts = models.ForeignKey(NUTS, related_name='+')

    class Meta:
        ordering = ('code',)
        verbose_name = 'LAU'
        verbose_name_plural = 'LAU'

    def __str__(self):
        return self.name

    @cached_property
    def nuts0(self):
        return NUTS.objects.get(code=self.nuts_id[:2])

    @cached_property
    def nuts1(self):
        return NUTS.objects.get(code=self.nuts_id[:3])

    @cached_property
    def nuts2(self):
        return NUTS.objects.get(code=self.nuts_id[:4])

    @cached_property
    def nuts3(self):
        if len(self.nuts_id) == 5:
            return self.nuts
        else:
            return NUTS.objects.get(code=self.nuts_id[:5])

    @cached_property
    def nuts4(self):
        return self.nuts if len(self.nuts_id) == 6 else None
