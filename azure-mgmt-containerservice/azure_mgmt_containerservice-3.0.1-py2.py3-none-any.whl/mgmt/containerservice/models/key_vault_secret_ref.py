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


class KeyVaultSecretRef(Model):
    """Reference to a secret stored in Azure Key Vault.

    :param vault_id: Key vault identifier.
    :type vault_id: str
    :param secret_name: The secret name.
    :type secret_name: str
    :param version: The secret version.
    :type version: str
    """

    _validation = {
        'vault_id': {'required': True},
        'secret_name': {'required': True},
    }

    _attribute_map = {
        'vault_id': {'key': 'vaultID', 'type': 'str'},
        'secret_name': {'key': 'secretName', 'type': 'str'},
        'version': {'key': 'version', 'type': 'str'},
    }

    def __init__(self, vault_id, secret_name, version=None):
        super(KeyVaultSecretRef, self).__init__()
        self.vault_id = vault_id
        self.secret_name = secret_name
        self.version = version
