from django.test import TestCase
import inspect
from django.db.models import Model as DjangoBaseModel
from adhara.models import AdharaModel


class ExtendsAdharaModel(TestCase):

    def __init__(self, models, method_name):
        self.models = models
        super(ExtendsAdharaModel, self).__init__(method_name)

    def test_models_in_app(self):
        if not self.models:
            return
        for name, obj in inspect.getmembers(self.models):
            if inspect.isclass(obj) and issubclass(obj, DjangoBaseModel):
                extends_adhara_model = issubclass(obj, AdharaModel)
                if not extends_adhara_model:
                    print(str(obj), "doesn't extend Adhara model")
                assert extends_adhara_model
