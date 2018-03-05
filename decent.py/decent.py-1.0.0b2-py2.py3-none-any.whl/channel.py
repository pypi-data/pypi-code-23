import requests
import sys

# static type checking, mainly for testing
# python versions <3.5 don't have this in the standard library,
# but they can be installed from pip. it's not a big deal if the
# user doesn't have `typing` - they just won't be able to run it
# through mypy.
try:
    from typing import Dict, List, Tuple, Any, Text, Optional
    Json = Dict[Text, Any]
except ImportError:
    pass

if sys.version_info[0] < 3:
    from urlparse import urljoin
else:
    from urllib.parse import urljoin

from .errors import DecentError


class Channel:
    def __init__(self, server, cid, name, unread_count = None):
        # type: (Any, str, str, Optional[int]) -> None
        self.server = server
        self.cid = cid
        self.name = name
        #self.pins = pins
        self.unread_count = unread_count


    @classmethod
    def from_json(cls, server, json):
        # type: (type, Any, Json) -> Channel
        "Creates a new channel object from the JSON returned by the Decent API."
        cid = json["id"]
        name = json["name"]
        unread_count = json.get("unreadMessageCount")
        if unread_count: unread_count = int(unread_count)

        # if "pinnedMessages" in json:
        #     pin_json = json["pinnedMessages"]
        # else:
        #     channel_data = server._request(requests.get, "channels/" + cid)
        #     pin_json = channel_data["channel"]["pinnedMessages"]
        # pins = [Message.from_json(server, j) for j in pin_json]

        return cls(server, cid, name, unread_count) # , pins


    def latest_messages(self, before=None, after=None, limit=None):
        # type: (Optional[str], Optional[str], Optional[int]) -> List[Any]
        "Gets latest messages in the channel."
        from .message import Message

        query = {} # type: Dict[Text, Any]
        if before: query["before"] = before
        if after: query["after"] = after
        if limit: query["limit"] = limit

        latest_messages = self.server._request(
            requests.get, "channels/" + self.cid + "/messages", query)
        messages = []
        for m in latest_messages["messages"]:
            messages.append(Message.from_json(self.server, m))
        return messages


    def send(self, text):
        # type: (Text) -> int
        "Sends a new message."
        m = self.server._request(requests.post, "messages", {
            "channelID": self.cid,
            "text": text
        })
        return m["messageID"]


    def rename(self, new_name):
        # type: (Text) -> None
        "Renames the channel."
        self.server._request(requests.patch, "channels/" + self.cid,
                             {"name": new_name})
        self.name = new_name


    def delete(self):
        # type: () -> None
        "Deletes the channel."
        self.server._request(requests.delete, "channels/" + self.cid)


    def mark_read(self):
        # type: () -> None
        "Marks the channel as read."
        self.server._request(requests.post, "channels/" + self.cid + "/mark-read")


    @property
    def pins(self):
        # type: () -> Tuple[Any, ...]
        from .message import Message
        json = self.server._request(requests.get, "channels/" + self.cid + "/pins")
        return tuple(Message.from_json(self.server, j) for j in json)


    @staticmethod
    def by_id(server, cid):
        # type: (str) -> Channel
        for channel in server.channels:
            if channel.cid == cid:
                return channel
                break
        else:
            raise DecentError("Channel with id {} not found".format(cid))
