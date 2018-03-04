import json
import sys
import re
import requests
import websocket

# static type checking, mainly for testing
# python versions <3.5 don't have this in the standard library,
# but they can be installed from pip. it's not a big deal if the
# user doesn't have `typing` - they just won't be able to run it
# through mypy.
try:
    from typing import Dict, List, Callable, Any, Text
    Json = Dict[Text, Any]
except ImportError:
    pass

if sys.version_info[0] < 3:
    from urlparse import urljoin
else:
    from urllib.parse import urljoin

from .errors import DecentError
from .channel import Channel
from .message import Message
from .user import User
from .emote import Emote


class Server:
    "The main class for a Decent server."
    def __init__(self, url, username, password):
        # type: (str, str, str) -> None
        self.url = url
        self.api_url = urljoin(url, "api/")
        self.pretty_url = url.split("//")[1].rstrip("/")
        self.username = username
        self.password = password
        self.channels = [] # type: List[Channel]
        self.users = []    # type: List[User]
        self.emotes = []   # type: List[Emote]
        self.socket = None

        # placeholder callbacks
        self.callbacks = {
            "on_message": lambda message: None,
            "on_edit": lambda message: None,
            "on_channel_new": lambda channel: None,
            "on_channel_update": lambda channel: None,
            "on_channel_delete": lambda channel: None,
            "on_pin_add": lambda message: None,
            "on_pin_remove": lambda mid: None,
            "on_user_online": lambda user: None,
            "on_user_offline": lambda user: None,
            "on_user_new": lambda user: None,
            "on_user_gone": lambda uid: None,
            "on_user_update": lambda user: None,
            "on_user_mention": lambda message: None,
            "on_user_unmention": lambda mid: None,
            "on_emote_new": lambda emote: None,
            "on_emote_delete": lambda shortcode: None
        }


    def connect(self):
        # type: () -> None
        "Connects to the server and initializes everything."

        # ping the server, to see if it's online
        ping = requests.get(self.api_url)
        if (ping.status_code == requests.codes.ok and
            "decentVersion" in ping.json()):
            # valid decent server
            pass
        elif ping.status_code in (requests.codes.ok, requests.codes.not_found):
            raise DecentError("{} is not a valid Decent server".format(
                self.url))
        else:
            raise DecentError("Could not connect to {} (error {})".format(
                self.url, ping.status_code))

        # login to server
        login_r = requests.post(urljoin(self.api_url, "sessions"), json={
            "username": self.username,
            "password": self.password
        })
        login_data = login_r.json()

        if "error" not in login_data:
            self.session_id = login_data["sessionID"]

            # get users
            users_data = self._request(requests.get, "users")
            currentuser_data = self._request(requests.get, "sessions/" + self.session_id)

            # add current user
            self.uid = currentuser_data["user"]["id"]
            self.user = User.from_json(self, currentuser_data["user"])
            self.users.append(self.user)

            # add other users
            print(users_data)
            for user in users_data["users"]:
                if user["id"] != self.uid:
                    self.users.append(User.from_json(self, user))

                print(self.users)
                

            # get channels
            channels = self._request(requests.get, "channels")["channels"]
            for channel in channels:
                self.channels.append(Channel.from_json(self, channel))

            # get emotes
            emotes = self._request(requests.get, "emotes")["emotes"]
            for emote in emotes:
                self.emotes.append(Emote.from_json(self, emote))

            # get server properties
            self.properties = self._request(requests.get, "properties")["properties"]
            print(self.properties)
        else:
            raise DecentError.success_false("/api/sessions", login_data)

        # create websocket
        if not self.socket:
            # wss or ws?
            self.secure = self.properties["useSecure"]
            protocol = "wss://" if self.secure else "ws://"

            self.socket = websocket.create_connection(protocol + self.pretty_url)
            #self.socket.sock.setblocking(0)


    def create_channel(self, name):
        # type: (str) -> Channel
        "Creates a new channel."
        channel_data = self._request(requests.post, "channels", {"name": name})
        return self.get_channel(channel_data["channelID"])


    def get_message(self, mid):
        # type: (str) -> Message
        "Gets a message from an ID."
        getm_data = self._request(requests.get, "messages/" + str(mid))
        return Message.from_json(self, getm_data["message"])


    def get_channel(self, cid):
        # type: (str) -> Channel
        "Gets a channel from an ID."
        getc_data = self._request(requests.get, "channels/" + str(cid))
        return Channel.from_json(self, getc_data["channel"])


    def get_user(self, uid):
        # type: (str) -> User
        "Gets a user from an ID."
        getu_data = self._request(requests.get, "users/" + str(uid))
        return User.from_json(self, getu_data["user"])


    def event(self, func):
        # type: (Callable[..., None]) -> None
        "Decorator for event callbacks."
        if func.__name__ in self.callbacks:
            self.callbacks[func.__name__] = func


    def mainloop(self):
        # type: () -> None
        "Recieves socket data and does stuff with it."

        if not self.socket:
            raise DecentError("Please call connect() before running the main loop.")

        message_data = self.socket.recv()
        message_json = json.loads(message_data)

        data = message_json.get("data")
        if message_json["evt"] == "pingdata":
            pong_data = json.dumps({"evt": "pongdata", "data": {
                "sessionID": self.session_id}})
            self.socket.send(pong_data)
        elif message_json["evt"] == "message/new":
            message = Message.from_json(self, data["message"])
            self.callbacks["on_message"](message)
        elif message_json["evt"] == "message/edit":
            message = Message.from_json(self, data["message"])
            self.callbacks["on_edit"](message)
        elif message_json["evt"] == "channel/new":
            channel_json = data["channel"]
            channel = Channel.from_json(self, channel_json)
            self.channels.append(channel)
            self.callbacks["on_channel_new"](channel)
        elif message_json["evt"] == "channel/update":
            channel = Channel.by_id(self, data["channelID"])
            channel.name = data["channel"]["name"]
            channel.unread_count = data["channel"]["unreadMessageCount"]
            self.callbacks["on_channel_update"](channel)
        elif message_json["evt"] == "channel/delete":
            channel = Channel.by_id(self, data["channelID"])
            self.channels.remove(channel)
            self.callbacks["on_channel_delete"](channel)
        elif message_json["evt"] == "channel/pins/add":
            message = Message.from_json(self, data["message"])
            self.callbacks["on_pin_add"](message)
        elif message_json["evt"] == "channel/pins/remove":
            self.callbacks["on_pin_remove"](data["messageID"])
        elif message.json["evt"] == "user/new":
            user = User.from_json(self, data["user"])
            self.users.append(user)
            self.callbacks["on_user_new"](user)
        elif message_json["evt"] == "user/gone":
            user = User.by_id(self, data["userID"])
            self.users.remove(user)
            self.callbacks["on_user_gone"](data["userID"])
        elif message_json["evt"] == "user/online":
            user = User.by_id(self, data["userID"])
            self.callbacks["on_user_online"](user)
        elif message_json["evt"] == "user/offline":
            user = User.by_id(self, data["userID"])
            self.callbacks["on_user_offline"](user)
        elif message_json["evt"] == "user/update":
            user = User.by_id(self, data["user"]["id"])
            new_user = User.from_json(self, data["user"])
            self.users[self.users.index(user)] = new_user
            self.callbacks["on_user_update"](user)
        elif message_json["evt"] == "user/mentions/add":
            message = Message.from_json(data["message"])
            self.callbacks["on_user_mention"](message)
        elif message_json["evt"] == "user/mentions/remove":
            self.callbacks["on_user_unmention"](data["messageID"])
        elif message_json["evt"] == "emote/new":
            emote = Emote.from_json(self, data["emote"])
            self.emotes.append(emote)
            self.callbacks["on_emote_new"](emote)
        elif message_json["evt"] == "emote/delete":
            emote = Emote.by_shortcode(self, data["shortcode"])
            self.emotes.remove(emote)
            self.callbacks["on_emote_delete"](data["shortcode"])



    def _request(self,
                 method, # type: Callable[..., requests.Response]
                 url,    # type: str
                 data={} # type: Json
                ):
        # type: (...) -> Json
        if method == requests.get:
            r = method(
                    urljoin(self.api_url, url),
                    data,
                    headers={"X-Session-ID": self.session_id})
        else:
            r = method(
                    urljoin(self.api_url, url),
                    json=data,
                    headers={"X-Session-ID": self.session_id})
        j = r.json()

        if "error" in j:
            raise DecentError("Request to {} was unsuccessful (error: {})"
                              .format(url, j["error"]))
        else:
            return j
