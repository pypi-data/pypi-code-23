from rest_framework import pagination
from rest_framework.response import Response


class SimpleLimitOffsetPagination(pagination.LimitOffsetPagination):

    def get_paginated_response(self, data):
        return Response(data)
