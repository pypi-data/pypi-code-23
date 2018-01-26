# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from importlib import import_module
import logging

from django.conf import settings
from django.core import urlresolvers
from django import shortcuts
import django.views.decorators.vary
from django.views.generic import TemplateView
from six.moves import urllib

import horizon
from horizon import base
from horizon import exceptions
from horizon import notifications

LOG = logging.getLogger(__name__)


MESSAGES_PATH = getattr(settings, 'MESSAGES_PATH', None)


def get_user_home(user):
    try:
        token = user.token
    except AttributeError:
        raise exceptions.NotAuthenticated()
    # Domain Admin, Project Admin will default to identity
    dashboard = None
    if token.project.get('id') is None or user.is_superuser:
        try:
            dashboard = horizon.get_dashboard('identity')
        except base.NotRegistered:
            pass

    if dashboard is None:
        dashboard = horizon.get_default_dashboard()

    return dashboard.get_absolute_url()


@django.views.decorators.vary.vary_on_cookie
def splash(request):
    if not request.user.is_authenticated():
        raise exceptions.NotAuthenticated()

    response = shortcuts.redirect(horizon.get_user_home(request.user))
    if 'logout_reason' in request.COOKIES:
        response.delete_cookie('logout_reason')
    if 'logout_status' in request.COOKIES:
        response.delete_cookie('logout_status')
    # Display Message of the Day message from the message files
    # located in MESSAGES_PATH
    if MESSAGES_PATH:
        notifications.process_message_notification(request, MESSAGES_PATH)
    return response


def get_url_with_pagination(request, marker_name, prev_marker_name, url_string,
                            object_id=None):
    if object_id:
        url = urlresolvers.reverse(url_string, args=(object_id,))
    else:
        url = urlresolvers.reverse(url_string)
    marker = request.GET.get(marker_name, None)
    if marker:
        return "{}?{}".format(url,
                              urllib.parse.urlencode({marker_name: marker}))

    prev_marker = request.GET.get(prev_marker_name, None)
    if prev_marker:
        return "{}?{}".format(url,
                              urllib.parse.urlencode({prev_marker_name:
                                                      prev_marker}))
    return url


class ExtensibleHeaderView(TemplateView):
    template_name = 'header/_header_sections.html'

    def get_context_data(self, **kwargs):
        context = super(ExtensibleHeaderView, self).get_context_data(**kwargs)
        header_sections = []
        config = getattr(settings, 'HORIZON_CONFIG', {})
        for view_path in config.get("header_sections", []):
            mod_path, view_cls = view_path.rsplit(".", 1)
            try:
                mod = import_module(mod_path)
            except ImportError:
                LOG.warning("Could not load header view: %s", mod_path)
                continue

            try:
                view = getattr(mod, view_cls)(request=self.request)
                response = view.get(self.request)
                rendered_response = response.render()
                packed_response = [view_path.replace('.', '-'),
                                   rendered_response.content]
                header_sections.append(packed_response)

            except Exception as e:
                LOG.warning("Could not render header %(path)s, exception: "
                            "%(exc)s", {'path': view_path, 'exc': e})
                continue

        context['header_sections'] = header_sections
        return context
