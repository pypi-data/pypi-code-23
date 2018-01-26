# Copyright 2016 - Nokia Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import json
import pecan

from oslo_log import log
from oslo_utils import encodeutils
from osprofiler import profiler
from pecan.core import abort

from vitrage.api.controllers.rest import RootRestController
from vitrage.api.policy import enforce
from vitrage.common.constants import TemplateStatus as TStatus
from vitrage.common.exception import VitrageError

LOG = log.getLogger(__name__)


@profiler.trace_cls("template controller",
                    info={}, hide_args=False, trace_private=False)
class TemplateController(RootRestController):

    @pecan.expose('json')
    def get_all(self):

        LOG.info('returns template list')

        enforce("template list",
                pecan.request.headers,
                pecan.request.enforcer,
                {})
        try:
            return self._get_templates()
        except Exception as e:
            to_unicode = encodeutils.exception_to_unicode(e)
            LOG.exception('failed to get template list %s', to_unicode)
            abort(404, to_unicode)

    @pecan.expose('json')
    def get(self, template_uuid):

        LOG.info('get template content')

        enforce("template show",
                pecan.request.headers,
                pecan.request.enforcer,
                {})

        try:
            return self._show_template(template_uuid)
        except Exception as e:
            to_unicode = encodeutils.exception_to_unicode(e)
            LOG.exception('failed to show template %s --> %s',
                          template_uuid,
                          to_unicode)
            abort(404, to_unicode)

    @pecan.expose('json')
    def delete(self, **kwargs):
        uuid = kwargs['uuid']
        LOG.info("delete template. uuid: %s", str(uuid))

        enforce("template delete",
                pecan.request.headers,
                pecan.request.enforcer,
                {})
        try:
            return self._delete(uuid)
        except Exception as e:
            LOG.exception('failed to delete template %s', e)
            abort(404, str(e))

    @pecan.expose('json')
    def put(self, **kwargs):
        templates = kwargs['templates']
        LOG.info("add template: %s", templates)

        enforce("template add",
                pecan.request.headers,
                pecan.request.enforcer,
                {})
        template_type = kwargs['template_type']

        try:
            return self._add(templates, template_type)
        except Exception as e:
            LOG.exception('failed to add template %s', e)
            abort(404, str(e))

    @pecan.expose('json')
    def post(self, **kwargs):

        LOG.info('validate template. args: %s', kwargs)

        enforce("template validate",
                pecan.request.headers,
                pecan.request.enforcer,
                {})

        templates = kwargs['templates']
        template_type = kwargs.get('template_type')

        try:
            return self._validate(templates, template_type)
        except Exception as e:
            to_unicode = encodeutils.exception_to_unicode(e)
            LOG.exception('failed to validate template(s) %s', to_unicode)
            abort(404, to_unicode)

    @classmethod
    def _get_templates(cls):
        try:
            templates = pecan.request.storage.templates.query()
            templates = [t for t in templates if t.status != TStatus.DELETED]
            templates.sort(key=lambda template: template.created_at)
            return [cls._db_template_to_dict(t) for t in templates]
        except Exception as e:
            to_unicode = encodeutils.exception_to_unicode(e)
            LOG.exception('failed to get template list %s ', to_unicode)
            abort(404, to_unicode)

    @staticmethod
    def _show_template(uuid):
        try:
            templates = pecan.request.storage.templates.query(uuid=uuid)
            if not templates:
                raise VitrageError("Template %s not found", uuid)
            return templates[0].file_content
        except Exception as e:
            to_unicode = encodeutils.exception_to_unicode(e)
            LOG.exception('failed to show template with uuid: %s ', to_unicode)
            abort(404, to_unicode)

    @staticmethod
    def _validate(templates, template_type):

        result_json = pecan.request.client.call(pecan.request.context,
                                                'validate_template',
                                                templates=templates,
                                                template_type=template_type)
        try:
            return json.loads(result_json)
        except Exception as e:
            to_unicode = encodeutils.exception_to_unicode(e)
            LOG.exception('failed to open template file(s) %s ', to_unicode)
            abort(404, to_unicode)

    @classmethod
    def _add(cls, templates, template_type):
        try:
            results = pecan.request.client.call(
                pecan.request.context,
                'add_template',
                templates=templates,
                template_type=template_type)
            return results
        except Exception as e:
            LOG.exception('failed to add template file %s ', e)
            abort(404, str(e))

    @classmethod
    def _db_template_to_dict(cls, template):
        return {
            "uuid": template.uuid,
            "name": template.name,
            "status": template.status,
            "date": template.created_at,
            "status details": template.status_details,
            "type": template.template_type,
        }

    @staticmethod
    def _delete(uuid):
        try:
            results = pecan.request.client.call(
                pecan.request.context,
                'delete_template',
                uuids=uuid)
            return results
        except Exception as e:
            LOG.exception('failed to delete template %s ', e)
            abort(404, str(e))
