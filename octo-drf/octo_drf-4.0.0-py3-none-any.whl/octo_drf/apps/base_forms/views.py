


from rest_framework import generics
from rest_framework import viewsets

from .models import FormMeta
from .serializers import FormMetaSerializer

registered_forms = []  # Список для регистрации форм


def get_view_name(cls):
    name = cls.__name__
    if name.rfind('View') > 0:
        return name[:name.rfind('View')].lower()
    return name.lower()


def register_form(func):
    """
    Декоратор для регистрации форм
    """
    name = get_view_name(func)
    registered_forms.append(name)
    return func


class FormCreateView(generics.CreateAPIView):
    """
    View для создания форм.
    Определяет url формы, для исключения путаницы в названиях
    """

    @classmethod
    def get_url(cls):
        return get_view_name(cls) + '/'


class FormMetaView(viewsets.ReadOnlyModelViewSet):

    lookup_field = 'form_name'
    queryset = FormMeta.objects.prefetch_related('fields_meta')
    serializer_class = FormMetaSerializer