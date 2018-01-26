# Copyright 2017 - Nokia
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

from oslo_log import log

from vitrage.evaluator.actions.recipes.execute_mistral import WORKFLOW
from vitrage.evaluator.base import is_function
from vitrage.evaluator.template_fields import TemplateFields
from vitrage.evaluator.template_validation.content.base import \
    ActionValidator
from vitrage.evaluator.template_validation.content.base import \
    get_content_correct_result
from vitrage.evaluator.template_validation.content.base import \
    get_content_fault_result
from vitrage.evaluator.template_validation.status_messages import status_msgs


LOG = log.getLogger(__name__)


class ExecuteMistralValidator(ActionValidator):

    @staticmethod
    def validate(action, definitions_index):
        properties = action[TemplateFields.PROPERTIES]

        if WORKFLOW not in properties or not properties[WORKFLOW]:
            LOG.error('%s status code: %s' % (status_msgs[133], 133))
            return get_content_fault_result(133)

        for key, value in properties.items():
            if not isinstance(value, dict) and is_function(value):
                LOG.error('%s status code: %s' % (status_msgs[137], 137))
                return get_content_fault_result(137)

        return get_content_correct_result()
