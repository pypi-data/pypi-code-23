from util.response import JsonResponse
from util.pagination import ForkNonePagination


class PaginateMixin():
    def pagination_response(self, queryset):
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        data = self.get_paginated_response(serializer.data).data
        return JsonResponse(data=data)

    def fork_pagination_response(self, queryset):
        self.pagination_class = ForkNonePagination
        return self.fork_pagination_response(queryset)


class CustomModelMxinin():

    @property
    def attributes(self):
        attr = {}

        for field in self._meta.get_fields():
            field_name = field.name
            attr[field_name] = getattr(self, field_name, None)
        return attr
