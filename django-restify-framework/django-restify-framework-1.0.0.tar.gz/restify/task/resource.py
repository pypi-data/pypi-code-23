# coding: utf-8

import traceback

from restify.http import status
from restify.http.response import ApiResponse
from restify.resource.base import Resource

from restify.task import api_task


class TaskResource(Resource):
    TASK_REGISTRY = api_task

    def post(self, request):
        post = request.POST

        try:
            return ApiResponse({
                'return': self.TASK_REGISTRY.dispatch_remote_call(post)
            })
        except Exception as e:
            return ApiResponse({
                'exception': traceback.format_exc()
            }, status_code=status.HTTP_400_BAD_REQUEST)
