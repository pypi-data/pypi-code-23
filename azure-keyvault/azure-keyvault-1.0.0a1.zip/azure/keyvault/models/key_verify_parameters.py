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


class KeyVerifyParameters(Model):
    """The key verify parameters.

    :param algorithm: The signing/verification algorithm. For more information
     on possible algorithm types, see JsonWebKeySignatureAlgorithm. Possible
     values include: 'PS256', 'PS384', 'PS512', 'RS256', 'RS384', 'RS512',
     'RSNULL'
    :type algorithm: str or :class:`JsonWebKeySignatureAlgorithm
     <azure.keyvault.models.JsonWebKeySignatureAlgorithm>`
    :param digest: The digest used for signing.
    :type digest: bytes
    :param signature: The signature to be verified.
    :type signature: bytes
    """

    _validation = {
        'algorithm': {'required': True, 'min_length': 1},
        'digest': {'required': True},
        'signature': {'required': True},
    }

    _attribute_map = {
        'algorithm': {'key': 'alg', 'type': 'str'},
        'digest': {'key': 'digest', 'type': 'base64'},
        'signature': {'key': 'value', 'type': 'base64'},
    }

    def __init__(self, algorithm, digest, signature):
        self.algorithm = algorithm
        self.digest = digest
        self.signature = signature
