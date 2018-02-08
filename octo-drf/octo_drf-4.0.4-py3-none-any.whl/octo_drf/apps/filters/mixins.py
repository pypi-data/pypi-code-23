from .filters import (
    field_list_filter, related_field_list_filter, bool_filter, range_filter, related_range_filter
)
"""
class Category(models.Model):
    name = models.TextField(
        'Название'
    )
    rating = models.IntegerField()


class Item(FilterMixin, models.Model):
    filters = [
        {
            'type': 'list', 'title': 'Имена', 'lookup_field': 'name', 'repr_type': 'list', 'name': 'name'
        },
        {
            'type': 'related_list', 'title': 'Категории',
            'lookup_field': {'prefix': 'category__', 'field': 'id'},
            'related_model': {'cls': Category, 'fields': ['id', 'name']},
            'name': 'categories',
            'repr_type': 'list'
        },
        {
            'type': 'bool', 'title': 'Показывать?', 'lookup_field': 'is_publish', 'repr_type': 'bool', 'name': 'is_publish'
        },
        {
            'type': 'range', 'title': 'Диапазон цен' 'lookup_field': 'price', 'repr_type': 'range', 'name': 'price'
        },
        {
            'type': 'related_range', 'title': 'Диапазон рейтинга категорий',
            'lookup_field': {'prefix': 'category__', 'field': 'rating'},
            'related_model': {'cls': Category},
            'name': 'rating_range',
            'repr_type': 'range'
        },
    ]
    
    name = models.TextField(
        'Название'
    )
    price = models.IntegerField()
    category = models.ForeignKey(
        Category,
        related_name='items'
    )
    is_publish = models.BooleanField()
"""


class FilterMixin:

    _filter_types = {
        'list': field_list_filter,
        'related_list': related_field_list_filter,
        'bool': bool_filter,
        'related_bool': bool_filter,
        'range': range_filter,
        'related_range': related_range_filter,
    }
    custom_filter_types = {}

    filters = []

    def get_filter_types(self):
        return {**self._filter_types, **self.custom_filter_types}

    def get_filters(self):
        filter_types = self.get_filter_types()
        response = {}

        for item in self.filters:
            name = item['name']
            filter_type = item['type']
            filter_function = filter_types.get(name) or filter_types.get(filter_type)

            response[name] = filter_function(self._meta.model, **item)

        return response
