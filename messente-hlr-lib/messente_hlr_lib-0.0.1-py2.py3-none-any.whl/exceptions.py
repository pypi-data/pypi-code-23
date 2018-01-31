"""
   Copyright 2018 Messente Communications Ltd.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""


class MessenteHlrError(Exception):
    """Base error class for all verigator related errors."""

    def __init__(self, code, message):
        super(MessenteHlrError, self).__init__(message)
        self.code = code
        self.message = message


class InvalidDataError(MessenteHlrError):
    """This error is raised when provided data is invalid"""
    pass


class WrongCredentialsError(MessenteHlrError):
    """This error raises when you provided invalid credentials.

    Please see messente dashboard for correct username and password
    """
    pass


class InternalError(MessenteHlrError):
    """This error means that there is a problem on the server side."""
    pass


class InvalidResponseError(MessenteHlrError):
    """This error usually raises when server returned non-json response"""
    pass


class NoSuchResourceError(MessenteHlrError):
    """This error is raised when the resource that yu were looking for does not exist"""
    pass


class ResourceAlreadyExistsError(MessenteHlrError):
    """This error is raised when you are creating resource that already exists"""
    pass


class ResourceForbiddenError(MessenteHlrError):
    """This error raises when you don't have permissions to access the resource"""
    pass
