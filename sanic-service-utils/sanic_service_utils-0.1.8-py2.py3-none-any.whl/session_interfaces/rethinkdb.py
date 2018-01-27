from typing import Dict
import uuid

from anji_orm import Model, JsonField
from sanic.request import Request
from sanic.response import HTTPResponse
from sanic_session.base import BaseSessionInterface, SessionDict


__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.1.8"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


class RethinkDBSession(Model):

    _table = 'sanic_sessions'

    session_data = JsonField()


class RethinkDBSessionInterface(BaseSessionInterface):
    def __init__(
            self, domain: str = None, expiry: int = 2592000,
            httponly: bool = True, cookie_name: str = 'session',
            sessioncookie: bool = False) -> None:
        """
        Initializes a session interface backed by RethinkDB and anji_orm.
        Args:
            domain (str, optional):
                Optional domain which will be attached to the cookie.
            expiry (int, optional):
                Seconds until the session should expire.
            httponly (bool, optional):
                Adds the `httponly` flag to the session cookie.
            cookie_name (str, optional):
                Name used for the client cookie.
            sessioncookie (bool, optional):
                Specifies if the sent cookie should be a 'session cookie', i.e
                no Expires or Max-age headers are included. Expiry is still
                fully tracked on the server side. Default setting is False.
        """
        self.expiry = expiry
        self.cookie_name = cookie_name
        self.domain = domain
        self.httponly = httponly
        self.sessioncookie = sessioncookie

    async def open(self, request: Request) -> Dict:
        """
        Opens a session onto the request. Restores the client's session from
        data stored in RethinkDB if one exists. The session data will be available on `request.session`
        Args:
            request (sanic.request.Request):
                The request, which a sessionwill be opened onto.
        Returns:
            dict:
                the client's session data,
                attached as well to `request.session`.
        """
        sid = request.cookies.get(self.cookie_name)

        if not sid:
            sid = uuid.uuid4().hex
            session_dict = SessionDict(sid=sid)
        else:
            val: RethinkDBSession = (await RethinkDBSession.async_execute(
                RethinkDBSession.all().get(sid)
            ))

            if val is not None:
                session_dict = SessionDict(val.session_data, sid=sid)
            else:
                session_dict = SessionDict(sid=sid)

        request['session'] = session_dict
        return session_dict

    async def save(self, request: Request, response: HTTPResponse) -> None:
        """
        Saves the session into RethinkDB and returns appropriate cookies.
        Args:
            request (sanic.request.Request):
                The sanic request which has an attached session.
            response (sanic.response.HTTPResponse):
                The Sanic response. Cookies with the appropriate expiration
                will be added onto this response.
        Returns:
            None
        """
        if 'session' not in request:
            return

        key = request['session'].sid
        if not request['session']:

            await RethinkDBSession.async_execute(
                RethinkDBSession.all().get(key).delete()
            )

            if request['session'].modified:
                self._delete_cookie(request, response)

            return

        val = dict(request['session'])

        await RethinkDBSession(id_=key, session_data=val).async_send()
        self._set_cookie_expiration(request, response)
