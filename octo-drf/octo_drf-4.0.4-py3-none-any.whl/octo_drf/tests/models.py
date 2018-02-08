


from mixer.backend.django import mixer

from .base import AbstractBaseTest


class AbstractModelTest(AbstractBaseTest):

    def test_init(self):
        obj = mixer.blend(self.get_model(), **self.get_empty_fields())
        assert obj.pk == 1, 'Должен сохранить экземпляр'
