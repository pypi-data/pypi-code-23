# Copyright 2018 - Nokia
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from oslo_log import log
from oslo_utils import uuidutils

from vitrage.common.constants import TemplateStatus
from vitrage.common.constants import TemplateTopologyFields as TFields
from vitrage.common.constants import TemplateTypes as TType
from vitrage.common.exception import VitrageError
from vitrage.evaluator.base import Template
from vitrage.evaluator import template_validation
from vitrage.evaluator.template_validation import base
from vitrage.storage.sqlalchemy import models

LOG = log.getLogger(__name__)

METADATA = 'metadata'
NAME = 'name'


def add_templates_to_db(db, templates, cli_type):
    db_rows = list()
    for template in templates:
        final_type = template[METADATA].get(TFields.TYPE, cli_type)
        if not final_type or (cli_type and cli_type != final_type):
            db_rows.append(_get_error_result(template, final_type,
                                             "Unknown template type"))
            continue

        result = _validate_template(db, template, final_type)
        if not _is_duplicate(db, template, result):
            db_row = _to_db_row(result, template, final_type)
            db.templates.create(db_row)
            db_rows.append(db_row)
        else:
            db_rows.append(_get_error_result(template, final_type,
                                             "Duplicate template name"))
    return db_rows


def validate_templates(db, templates, cli_type):
    results = list()
    for template in templates:
        final_type = template[METADATA].get(TFields.TYPE, cli_type)
        if not final_type or (cli_type and cli_type != final_type):
            results.append(base.Result("", False, "", "Unknown template type"))
        else:
            results.append(_validate_template(db, template, final_type))
    return results


def _validate_template(db, template, template_type):
    if template_type == TType.DEFINITION:
        result = template_validation.validate_definition_template(template)
    elif template_type == TType.STANDARD:
        result = template_validation.validate_template(template,
                                                       _load_def_templates(db))
    elif template_type == TType.EQUIVALENCE:
        result = base.Result("", True, "", "No Validation")
    else:
        raise VitrageError("Unknown template type %s", template_type)
    return result


def _is_duplicate(db, template, result):
    if result.is_valid_config:
        template_name = template[METADATA][NAME]
        templates = db.templates.query(name=template_name)
        if [t for t in templates if t.status != TemplateStatus.DELETED]:
            return True


def _get_error_result(template, template_type, msg):
    return models.Template(
        name=template[METADATA][NAME],
        uuid="",
        status=TemplateStatus.ERROR,
        status_details=msg,
        file_content=template,
        template_type=template_type)


def _to_db_row(result, template, template_type):
    uuid = uuidutils.generate_uuid()
    status = TemplateStatus.LOADING if result.is_valid_config else \
        TemplateStatus.ERROR
    status_details = result.comment
    return models.Template(
        name=template[METADATA][NAME],
        uuid=uuid,
        status=status,
        status_details=status_details,
        file_content=template,
        template_type=template_type)


def _load_def_templates(db):
    def_templates = {}
    items = db.templates.query(template_type=TType.DEFINITION)
    def_templates_db = [x for x in items if x.status in [
                        TemplateStatus.ACTIVE,
                        TemplateStatus.LOADING]]
    for df in def_templates_db:
        def_templates[df.uuid] = Template(df.uuid,
                                          df.file_content,
                                          df.created_at)
    return def_templates
