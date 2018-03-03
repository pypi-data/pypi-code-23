import logging
from typing import Type  # NOQA

from zsl import inject
from zsl.db.model.app_model import AppModel
from zsl.router.task import TaskConfiguration

from zsl_openapi.api import ApiDescription  # NOQA
from zsl_openapi.api import ApiModelDefinition
from zsl_openapi.api import ApiModelProperty
from zsl_openapi.api import ApiOperation
from zsl_openapi.api import ApiPathItem
from zsl_openapi.api import ApiResponse
from zsl_openapi.builders import ApiDescriptionBuilder
from zsl_openapi.decorators import get_metadata


class TasksApiDescriptionBuilder(ApiDescriptionBuilder):
    @inject(task_configuration=TaskConfiguration)
    def __init__(self, task_configuration):
        # type: (TaskConfiguration)->None
        self._task_configuration = task_configuration  # type: TaskConfiguration

    def build(self, api_description):
        # type: (ApiDescription)->None
        for namespace in self._task_configuration.namespaces:
            for route, task in namespace.get_routes().items():
                if hasattr(task, 'Request'):
                    request_class = task.Request
                    request_ref = self._build_model(request_class, api_description)
                else:
                    request_ref = None

                if hasattr(task, 'Response'):
                    response_class = task.Response
                    response_ref = self._build_model(response_class, api_description)
                else:
                    response_ref = None

                url = namespace.namespace + '/' + route
                url = '/' + url.lstrip('/')
                logging.getLogger(__name__).info("Generating task at url '{0}'.".format(url))
                meta = get_metadata(task)

                path_item = ApiPathItem()
                path_item.post = ApiOperation()
                path_item.post.tags = meta.tags
                path_item.post.summary = meta.summary
                path_item.post.description = task.__doc__.strip() if task.__doc__ is not None else None
                path_item.post.operation_id = meta.operation_id or url[url.rfind("/") + 1:]
                if not path_item.post.description:
                    path_item.post.description = path_item.post.summary

                if request_ref:
                    path_item.post.parameters = [
                        {
                            "in": "body",
                            "name": "body",
                            "description": "Request",
                            "required": True,
                            "schema": {
                                "$ref": request_ref
                            }
                        }
                    ]

                    path_item.post.request_body = {
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': request_ref
                                }
                            }
                        }
                    }

                if response_ref:
                    response = ApiResponse()
                    response.content = 'application/json'
                    response.schema = {"$ref": response_ref}
                    path_item.post.set_response(200, response)

                api_description.set_path(url, path_item)

    def _build_model(self, model_cls, api_description):
        # type: (Type, ApiDescription)->str
        # Each AppModel definition is created by
        # `:class:zsl_openapi.builders.models.PersistentModelsApiDescriptionBuilder`
        if issubclass(model_cls, AppModel):
            return "#/definitions/{0}".format(model_cls.__name__)

        model_definition = ApiModelDefinition()
        model_definition.name = model_cls.__name__
        model_definition.type = "object"
        for model_property in model_cls().__dict__:
            model_property_definition = ApiModelProperty()
            model_property_definition.name = model_property
            model_property_definition.type = "string"
            model_definition.add_property(model_property_definition)
        api_description.add_model_definition(model_definition)
        return "#/definitions/{0}".format(model_cls.__name__)
