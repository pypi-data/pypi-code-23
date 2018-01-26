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

from .secret_item import SecretItem


class DeletedSecretItem(SecretItem):
    """The deleted secret item containing metadata about the deleted secret.

    Variables are only populated by the server, and will be ignored when
    sending a request.

    :param id: Secret identifier.
    :type id: str
    :param attributes: The secret management attributes.
    :type attributes: :class:`SecretAttributes
     <azure.keyvault.models.SecretAttributes>`
    :param tags: Application specific metadata in the form of key-value pairs.
    :type tags: dict
    :param content_type: Type of the secret value such as a password.
    :type content_type: str
    :ivar managed: True if the secret's lifetime is managed by key vault. If
     this is a key backing a certificate, then managed will be true.
    :vartype managed: bool
    :param recovery_id: The url of the recovery object, used to identify and
     recover the deleted secret.
    :type recovery_id: str
    :ivar scheduled_purge_date: The time when the secret is scheduled to be
     purged, in UTC
    :vartype scheduled_purge_date: datetime
    :ivar deleted_date: The time when the secret was deleted, in UTC
    :vartype deleted_date: datetime
    """

    _validation = {
        'managed': {'readonly': True},
        'scheduled_purge_date': {'readonly': True},
        'deleted_date': {'readonly': True},
    }

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'attributes': {'key': 'attributes', 'type': 'SecretAttributes'},
        'tags': {'key': 'tags', 'type': '{str}'},
        'content_type': {'key': 'contentType', 'type': 'str'},
        'managed': {'key': 'managed', 'type': 'bool'},
        'recovery_id': {'key': 'recoveryId', 'type': 'str'},
        'scheduled_purge_date': {'key': 'scheduledPurgeDate', 'type': 'unix-time'},
        'deleted_date': {'key': 'deletedDate', 'type': 'unix-time'},
    }

    def __init__(self, id=None, attributes=None, tags=None, content_type=None, recovery_id=None):
        super(DeletedSecretItem, self).__init__(id=id, attributes=attributes, tags=tags, content_type=content_type)
        self.recovery_id = recovery_id
        self.scheduled_purge_date = None
        self.deleted_date = None
