from django.db import models


class Instrument(models.Model):
    name = models.CharField(max_length=30)


class TestManager(models.Manager):
    def create_test_data(self):
        for p in [
                ("Fred", "Flintstone", 30, "guitar"),
                ("Wilma", "Flintstone", 28, None),
                ("Barney", "Rubble", 25, None),
                ("Betty", "Rubble", 25, None),
                ("Pebbles", "Flintstone", 3, None)]:
            if p[3]:
                i = Instrument.objects.create(name=p[3])
            Person.objects.create(first_name=p[0], last_name=p[1], age=p[2], instrument=i)


class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    age = models.PositiveIntegerField(default=10)
    instrument = models.ForeignKey(Instrument, models.CASCADE, blank=True, null=True)

    objects = TestManager()

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)
