from dal.autocomplete import Select2QuerySetView

from cities.contrib.utils import get_cities_models


class PlaceNameStartsWithAutocompleteMixin(object):
    def get_queryset(self):
        qs = self.model.objects.all()

        if self.q:
            qs = qs.filter(Q(name__istartswith=self.q) |
                           Q(alt_names__name__istartswith=self.q))
        else:
            qs = qs[:100]

        return qs


class PlaceNameContainsAutocompleteMixin(object):
    def get_queryset(self):
        qs = self.model.objects.all()

        if self.q:
            qs = qs.filter(Q(name__icontains=self.q) |
                           Q(alt_names__name__icontains=self.q))
        else:
            qs = qs[:100]

        return qs


__all__ = []
for cities_model in get_cities_models():
    model_name = cities_model.__class__._name__

    startswith_autocomplete_name = '{model_name}NameStartsWithAutocomplete'.format(model_name)
    locals()[startswith_autocomplete_name] = type(
        startswith_autocomplete_name,
        (PlaceNameStartsWithAutocompleteMixin,),
        {'model': cities_model})

    contains_autocomplete_name = '{model_name}NameContainsAutocomplete'.format(model_name)
    locals()[contains_autocomplete_name] = type(
        contains_autocomplete_name,
        (PlaceNameContainsAutocompleteMixin,),
        {'model': cities_model})

    __all__.extend([startswith_autocomplete_name, contains_autocomplete_name])
