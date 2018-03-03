# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

import threading

from django.core.urlresolvers import Resolver404, resolve
from django.http import HttpResponse

import tcell_agent
from tcell_agent.agent import TCellAgent, PolicyTypes
from tcell_agent.appsensor.django import django_meta, django_request_response_appsensor
from tcell_agent.instrumentation import safe_wrap_function
from tcell_agent.instrumentation.djangoinst.routes import get_route_table, make_route_table
from tcell_agent.instrumentation.djangoinst.utils import django15or16, isDjango15
from tcell_agent.tcell_logger import get_module_logger


def set_route_id_for_request(request):
    route_table = get_route_table()
    try:
        if isDjango15:
            current_info = resolve(request.path_info)
            request._tcell_context.route_id = route_table.get(current_info.func, {}).get("route_id")
        elif django15or16 is False and request.resolver_match:
            request._tcell_context.route_id = route_table.get(request.resolver_match.func, {}).get("route_id")
    except Resolver404:
        pass
    except Exception as route_ex:
        LOGGER = get_module_logger(__name__)
        LOGGER.debug("Unknown resolver error {e}".format(e=route_ex))
        LOGGER.debug(route_ex, exc_info=True)


def assign_route_id(request):
    if request._tcell_context.route_id is None:
        set_route_id_for_request(request)


def assign_path_dictionary_for_request(request, path_dict):
    rust_policies = TCellAgent.get_policy(PolicyTypes.RUST)
    if rust_policies and rust_policies.appfirewall_enabled:
        meta = django_meta(request)
        meta.path_parameters_data(path_dict)


route_table_send_lock = threading.Lock()


def ensure_routes_sent():
    route_table_send_lock.acquire()
    if tcell_agent.instrumentation.djangoinst.app._route_table_sent:
        route_table_send_lock.release()
        return

    else:
        tcell_agent.instrumentation.djangoinst.app._route_table_sent = True
        route_table_send_lock.release()

    make_route_table()


class TCellLastMiddleware(object):

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)

        response = self.get_response(request)

        return self.process_response(request, response)

    def process_request(self, request):
        if not tcell_agent.instrumentation.djangoinst.app._route_table_sent:
            ensure_routes_sent()

    def process_view(self, request, view_func, view_args, view_kwargs):
        safe_wrap_function("Assiging route ID to route (view)", assign_route_id, request)

        if view_kwargs:
            safe_wrap_function("AppSensor Path Parameters",
                               assign_path_dictionary_for_request,
                               request,
                               view_kwargs)

        return None

    def process_template_response(self, request, response):
        safe_wrap_function("Assiging route ID to route (template)", assign_route_id, request)
        return response

    def process_response(self, request, response):
        safe_wrap_function("Assiging route ID to route (resp)", assign_route_id, request)
        safe_wrap_function("AppSensor Request/Response",
                           django_request_response_appsensor,
                           HttpResponse,
                           request,
                           response)
        return response
