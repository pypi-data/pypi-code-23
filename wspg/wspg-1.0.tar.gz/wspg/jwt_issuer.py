#
#   Copyright 2018 University of Lancaster
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import jwt

from .errors import ClientLeakableError


class JWTIssuer:
    def __init__(self, application, path):
        self.application = application
        self.path = path

        self.config = application.config[path]

        self.required_claims = [claim.strip() for claim in self.config['required-claims'].split(',')]

    def decode(self, token):
        try:
            claims_set = jwt.decode(token, self.config['secret'])
        except jwt.InvalidTokenError as e:
            raise ClientLeakableError("JWT decode error: {}".format(e)) from e

        for required_claim in self.required_claims:
            if required_claim not in claims_set:
                msg = "JWT claim set missing required claim {!r}"
                raise ClientLeakableError(msg.format(required_claim))

        return claims_set
