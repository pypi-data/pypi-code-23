from unittest import TestCase
from restclients_core import models


class TestModelString(TestCase):
    def test_model_string(self):
        class ModelTest(models.Model):
            number = models.CharField(max_length=8)
            one = models.IntegerField()

        m = ModelTest(number="number", one=1)
        self.assertEquals("%s" % m, "number: number, one: 1")
