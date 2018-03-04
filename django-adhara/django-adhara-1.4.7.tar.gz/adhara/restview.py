from itertools import chain
import importlib
from .exceptions import AdharaException
from .request import AdharaRequest, APIMethods
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db import utils as django_utils
from .utilities import is_reference_field
from django.views.generic import View

from .models.base_models import fill_ref_models
from .response import AdharaResponse, ResponseStatus
from .session import Session
from .utilities import get_user_model
import logging

logger = logging.getLogger("adhara.restview.RestView")


class RestView(View):
    """
    Rest view to handle API responses in a REST Pattern.
    _meta pattern for get_list
    _meta : {
        "page": {
            "start" : "1",
            "end": "10"
        }
    }
    """

    model = None

    def __init__(self, adhara_request=None, **kwargs):
        self._request = None
        self._db = None
        self._response = None
        if isinstance(adhara_request, AdharaRequest):
            self.set_api_request(adhara_request)
        super(RestView, self).__init__(**kwargs)

    def set_api_request(self, adhara_request):
        self._request = adhara_request
        if not getattr(adhara_request, "transformer", None):
            adhara_request.transformer = self._transform_row
        if not getattr(adhara_request, "list_transformer", None):
            adhara_request.list_transformer = self._list_transformer
        self._db = adhara_request.get_tenant_db()
        self._response = AdharaResponse(self._request)

    def _get_query_criteria(self):
        return self._request.get_criteria_object().get_criteria()

    def _get_exclude_criteria(self):
        return self._request.get_exclude_criteria_object().get_criteria()

    def _get_object(self, *fields):
        criteria = self._request.get_criteria_object().get_criteria()
        try:
            if len(fields):
                return self._request.get_model_manager().values(*fields).using(self._db).get(**criteria)
            else:
                return self._request.get_model_manager().using(self._db).get(**criteria)
        except ObjectDoesNotExist:
            return None

    def pre_authorize(self, request):
        """
        any validations like licensing check etc to be handled here
        :param {AdharaRequest} request: adhara request
        :return:
        """
        pass

    def _pre_process(self, *args, **kwargs):
        args_from_path = {}
        for key, value in kwargs.items():
            if key == "pk":
                self._request.set_identifier(kwargs["pk"])
            elif key.startswith("q_"):
                args_from_path[key[2:]] = value

        if not self._request.get_model():
            self._request.set_model(self.model)

        user_model = get_user_model()
        opts = self._request.get_model()._meta
        for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
            if is_reference_field(f) and user_model == f.model._meta.get_field(f.name).rel.to:
                try:
                    self._request.get_input()[f.name]
                except KeyError:
                    if self._request.get_method() in [APIMethods.POST, APIMethods.PUT, APIMethods.DELETE]:
                        args_from_path[f.name] = Session.get_user_id(self._request.get_http_request())

        if args_from_path:
            if self._request.get_method() in [APIMethods.POST]:
                self._request.update_input(args_from_path)
            self._request.get_criteria_object().update_criteria(criteria=args_from_path)

    def pre_process(self, api_request):
        """
        modify the request bu adding sub requests, or change the input data, etc.
        :param api_request: adhara.request.AdharaRequest
        :return: None
        """
        pass

    def authorize_crud(self, method, instance):
        """
        Authorize CRUD methods on the current view
        :param method: APIMethod
        :param instance: model entry
        :return:{bool} whether method is authorized or not
        """
        pass

    def authorize(self, request, instance=None, parent_instance=None):
        """
        :raises:{AdharaException}
        """
        pass

    def process(self):
        """
        executes related http method and returns an AdharaResponse object
        :return:{AdharaRequest}
        """
        return getattr(self, self._request.get_method().value.lower())()

    def _transform_row(self, row, transformed_row):
        self._get_permissions(row)
        self.transform_row(row, transformed_row)

    def transform_row(self, row, transformed_row):
        """
        modify a row data which will be returned in the response
        :param row: Django db entry instance
        :param transformed_row: Transformed row data in dict format
        :return: None
        """
        pass

    def _list_transformer(self, entries, transformed_data):
        self.list_transformer(entries, transformed_data)

    def list_transformer(self, entries, transformed_data):
        """
        Use this to transform list data
        :param entries: getlist model instance
        :param transformed_data: transformed list data
        :return: {*} return value will be set as list response. Return None to return default'ly transformed data
        """
        pass

    def _post_process(self):
        """
        holder to add code for post processing by rest view.
        Currently handle's adding permissions
        :return: None
        """
        # self._get_permissions()
        pass

    def post_process(self, response, success):
        """
        can handle methods after processing current adhara request
        :param response: AdharaResponse
        :param {bool} success: whether the request executed successfully
        :return:None
        """
        pass

    def _get_permissions(self, instance):
        """
        Constructs permissions and sets it to response object
        :return:None
        """
        # Post.like_set.rel.related_model
        # Post._meta.related_objects[0].related_model.Adhara.rest_view
        for operation in (APIMethods.PUT, APIMethods.DELETE):
            self._response.set_permission(
                instance.pk,
                "edit" if operation == APIMethods.PUT else operation.value.lower(),
                self.authorize_crud(operation, instance))

        for ro in self._request.get_model()._meta.related_objects:
            rest_view_class = RestView.get_rest_view_class_for_model(ro.related_model)
            related_field_name = ro.related_model._meta.object_name.lower()
            related_adhara_request = \
                AdharaRequest(self._request.get_http_request(), model=ro.related_model, method=APIMethods.POST)
            related_rv = rest_view_class(related_adhara_request)
            try:
                related_rv.authorize(related_adhara_request, parent_instance=instance)
                self._response.set_permission(instance.pk, related_field_name, True)
            except AdharaException:
                self._response.set_permission(instance.pk, related_field_name, False)

    @staticmethod
    def get_rest_view_class_for_model(model):
        try:
            related_rest_view = model.Adhara.rest_view
            if not related_rest_view:
                return
        except AttributeError:
            return
        splits = related_rest_view.split(".")
        return getattr(importlib.import_module(".".join(splits[0:-1])), splits[-1])

    def _extract_required_fields(self, instance):
        opts = instance._meta
        required_fields = self._request.get_meta().get_required_fields()
        for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
            if required_fields and f.name not in required_fields:
                try:
                    delattr(instance, f.name)
                except AttributeError as ae:
                    logger.debug(ae)
        return instance

    def get_count(self):
        self._response.success(
            self._request.get_model_manager().using(self._db).filter(**self._get_query_criteria()).count())
        return self._response

    def get_exists(self):
        self._response.success(self._get_object("pk") is not None)
        return self._response

    def post(self):
        with transaction.atomic(using=self._db):
            input_data = self._request.get_input()
            entry = self._request.get_model()(**input_data)
            self.authorize(self._request, instance=entry)
            try:
                entry.save(using=self._db)
            except django_utils.DatabaseError as e:
                self._response.error(e.args[1])
                return self._response
            # self._request.NEW_PRIMARY_KEY = entry.pk    # TODO
        self._response.success(self._extract_required_fields(entry))
        return self._response

    def get(self):
        entry = self._get_object()
        self.authorize(self._request, instance=entry)
        if entry is None:
            self._response.error("Invalid identifier")
        else:
            self._response.success(self._extract_required_fields(entry))
        return self._response

    def get_list(self):
        # TODO required fields
        qs = self._request.get_model_manager().using(self._db)\
            .exclude(**self._get_exclude_criteria())\
            .filter(**self._get_query_criteria())
        order_by = self._request.get_meta().get_order_by()
        if order_by:
            qs = qs.order_by(*order_by)
        total_count = len(qs)
        meta = self._request.get_meta()
        pagination = meta.get_pagination()
        curr_page = pagination.get_current_page()
        qs = qs[curr_page.get_start()-1: curr_page.get_end()]
        count = len(qs)
        meta.update_page_properties(count, total_count)
        for q in qs:
            self.authorize(self._request, instance=q)
        self._response.success(qs)
        return self._response

    def _put(self, entry):
        self.authorize(self._request, instance=entry)
        filled_input = fill_ref_models(entry, **self._request.get_input())
        for key, value in filled_input.items():
            setattr(entry, key, value)
        try:
            entry.save()
        except django_utils.DatabaseError as e:
            self._response.error(e.args[1])
        self._response.success(self._extract_required_fields(entry))
        return self._response

    def put(self):
        with transaction.atomic(using=self._db):
            entry = self._get_object()
            if entry is None:
                self._response.error("Does not exist")
            return self._put(entry)

    def put_or_create(self):
        with transaction.atomic(using=self._db):
            entry = self._get_object()
            if entry is None:
                return self.post()
            return self._put(entry)

    def delete(self):
        try:
            entry = self._request.get_model_manager().using(self._db).get(**self._get_query_criteria())
            self.authorize(self._request, instance=entry)
            entry.delete()
            self._response.success("Deleted Successfully")
        except django_utils.DatabaseError as e:
            self._response.error(e.args[1])
        return self._response

    def bulk_delete(self):
        try:
            entries = self._request.get_model_manager().using(self._db).filter(**self._get_query_criteria())
            for entry in entries:
                self.authorize(self._request, instance=entry)
            entries.delete()
            self._response.success("Deleted Successfully")
        except django_utils.DatabaseError as e:
            self._response.error(e.args[1])
        return self._response

    def execute(self, *args, **kwargs):
        try:
            self.pre_authorize(self._request)
        except AdharaException:
            self._response.error("Unauthorized")
            return self._response.serialize()
        try:
            self._pre_process(*args, **kwargs)
            self.pre_process(self._request)
            response = self.process()
            response.transform_data()
            self._post_process()
            self.post_process(self._response, self._response.get_response_status() == ResponseStatus.SUCCESS)
        except AdharaException as ae:
            self._response.error(ae.get_message())
            return self._response.serialize()
        return response.serialize()

    def dispatch(self, request, *args, **kwargs):
        self.set_api_request(request.adhara_request)
        return self.execute(*args, **kwargs)
