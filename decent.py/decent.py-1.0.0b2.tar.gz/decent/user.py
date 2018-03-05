import requests
import sys

# static type checking, mainly for testing
# python versions <3.5 don't have this in the standard library,
# but they can be installed from pip. it's not a big deal if the
# user doesn't have `typing` - they just won't be able to run it
# through mypy.
try:
    from typing import Dict, Any, Text, Optional
    Json = Dict[Text, Any]
except ImportError:
    pass

if sys.version_info[0] < 3:
    from urlparse import urljoin
else:
    from urllib.parse import urljoin

from .errors import DecentError


class User:
    def __init__(self,
                 server,         # type: Any
                 uid,            # type: str
                 username,       # type: str
                 perm_level,     # type: str
                 flair,          # type: str
                 online,         # type: bool
                 avatar_url,     # type: str
                 email=None,     # type: Optional[str]
                 authorized=None # type: Optional[bool]
                ):
        # type: (...) -> None
        self.server = server
        self.uid = uid
        self.username = username
        self.perm_level = perm_level
        self.flair = flair
        self.online = online
        self.avatar_url = avatar_url
        self.email = email
        self.authorized = authorized


    @classmethod
    def from_json(cls, server, json):
        # type: (type, Any, Json) -> User
        uid = json["id"]
        username = json["username"]
        perm_level = json["permissionLevel"]
        flair = json["flair"]
        online = json["online"]
        avatar_url = json["avatarURL"]
        email = json.get("email")
        authorized = json.get("authorized")

        return cls(server, uid, username, perm_level, flair, online, avatar_url,
                   email, authorized)


    @staticmethod
    def by_id(server, uid):
        # type: (Any, str) -> User
        for user in server.users:
            if user.uid == uid:
                return user
                break
        else:
            raise DecentError("User with id {} not found".format(uid))


    def authorize(self):
        # type: () -> None
        "Authorizes the user."
        self.server._request(requests.post, "authorize-user", {"userID": self.uid})


    def deauthorize(self):
        # type: () -> None
        "Deauthorizes the user."
        self.server._request(requests.post, "deauthorize-user", {"userID": self.uid})
