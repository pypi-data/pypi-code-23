from rest_framework import viewsets

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


class BaseModelViewSet(viewsets.ModelViewSet):
    """
    Базовый ModelViewSet
    """


class BaseReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Базовый ReadOnlyModelViewSet
    """
