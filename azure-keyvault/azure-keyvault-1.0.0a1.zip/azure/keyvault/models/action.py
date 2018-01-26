# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class Action(Model):
    """The action that will be executed.

    :param action_type: The type of the action. Possible values include:
     'EmailContacts', 'AutoRenew'
    :type action_type: str or :class:`ActionType
     <azure.keyvault.models.ActionType>`
    """

    _attribute_map = {
        'action_type': {'key': 'action_type', 'type': 'ActionType'},
    }

    def __init__(self, action_type=None):
        self.action_type = action_type
