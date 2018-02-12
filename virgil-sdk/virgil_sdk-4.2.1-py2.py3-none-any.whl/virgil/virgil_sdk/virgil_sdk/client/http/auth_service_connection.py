# Copyright (C) 2016-2018 Virgil Security Inc.
#
# Lead Maintainer: Virgil Security Inc. <support@virgilsecurity.com>
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     (1) Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
#     (2) Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#
#     (3) Neither the name of the copyright holder nor the names of its
#     contributors may be used to endorse or promote products derived from
#     this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ''AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from virgil_sdk.client.http.base_connection import BaseConnection


class AuthServiceConnection(BaseConnection):
    """Identity service connection class.

        Contains identity service specific errors dictionary.
        """

    def __init__(self, access_token, base_url):
        super(AuthServiceConnection, self).__init__(access_token, base_url)
        self._errors = {
            10000: "Internal application error. You know, shit happens, so do internal server errors.Just take a deep breath and try harder.",
            53000: "The resource owner id validation failed",
            53010: "The Virgil card specified by id doesn't exist on the Virgil Card service",
            53011: "The Auth service cannot get access to the Virgil card specified by id.The card in application scope and can't be retrieved",
            53020: "Encrypted message validation failed",
            53030: "The authentication attempt instance has expired already",
            53040: "Grant type is not supported as it is outside of the list: ['authorization_code']",
            53050: "Unable to find an authorization attempt by the specified code",
            40150: "Identity's token has expired",
            53060: "An authorization code has expired already",
            53070: "An authorization code was used previously",
            53080: "The Access code is invalid",
            53090: "The Refresh token not found",
            53100: "The Resource owner's Virgil card not verified"
        }
