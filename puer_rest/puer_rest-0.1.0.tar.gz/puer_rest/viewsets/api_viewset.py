import asyncio
from math import ceil

from aiohttp import hdrs
from puer_rest.exceptions import APINotFound, APIBadRequest

from puer_rest.views import APIView
from modules.auth.documents import UserExist

__all__ = ["APIViewSet"]


class APIViewSet(APIView):
    filter_set_schema = None

    method_map = {
        "get": {
            None: "list_view",
            "detail": "detail_view"
        },
        "post": {
            None: "create_view",
            "detail": None
        },
        "put": {
            None: None,
            "detail": "update_view"
        },
        "delete": {
            None: None,
            "detail": "delete_view"
        }
    }

    @property
    def _list_filters(self):
        if self.filter_set_schema is not None:

            filters = self.filter_set_schema().load(self.request.query)

            if any(filters.errors):
                raise APIBadRequest({"filters": filters.errors})
            return filters.data
        return {}

    async def list_view(self):
        serializer = self.get_serializer()
        filters = self._list_filters
        # Sorting
        sort_field = self.request.query.get("sort_field", "_id")
        try:
            sort_direction = int(self.request.query.get("sort_direction", -1))
        except ValueError:
            sort_direction = -1
        # Paginator
        page = int(self.request.query.get("page", 0))
        page_size = int(self.request.query.get("page_size", 20))

        object_list = serializer.list(filters, page, page_size, (sort_field, sort_direction))
        objects_count = await serializer.count(filters)
        pages_count = ceil(objects_count / page_size)
        result = []
        async for obj in await object_list:
            result.append(await serializer.to_representation(obj))

        return self.response(
            {
                "result": result,
                "page": page,
                "page_size": page_size,
                "count": objects_count,
                "pages_count": pages_count
            }
        )

    async def detail_view(self):
        serializer = self.get_serializer()
        obj = await serializer.get(self.request["detail_id"])
        if obj is None:
            raise APINotFound
        res = await serializer.to_representation(obj)
        return self.response(res)

    async def create_view(self):
        serializer = self.get_serializer()
        obj = await serializer.create(self.validated_data)
        res = await serializer.to_representation(obj)
        res["_created"] = True
        return self.response(res)

    async def update_view(self):
        serializer = self.get_serializer()
        obj = await serializer.get(self.request["detail_id"])
        if obj is None:
            raise APINotFound
        updated_obj = await serializer.update(obj, self.validated_data)
        res = await serializer.to_representation(updated_obj)
        res["_updated"] = True
        return self.response(res)

    async def delete_view(self):
        serializer = self.get_serializer()
        deleted = await serializer.delete(self.request["detail_id"])
        return self.response(
            {
                "id": self.request["detail_id"],
                "deleted": deleted
            }
        )

    def get_detail_method(self, method_variants):
        return method_variants.get("detail")

    def get_none_method(self, method_variants):
        return method_variants.get(None)

    def get_method(self):
        method = self.request._method.lower()
        detail = True if self.request.get("detail_id") else None
        method_variants = self.method_map.get(method)
        if method_variants:
            if detail:
                return self.get_detail_method(method_variants)
            else:
                return self.get_none_method(method_variants)
        else:
            return self.request._method.lower()

    async def dispatch(self):
        self.request["detail_id"] = self.request.match_info.get('id')
        return await super().dispatch()
