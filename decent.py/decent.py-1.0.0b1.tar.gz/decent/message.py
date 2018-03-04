import requests
import datetime

# static type checking, mainly for testing
# python versions <3.5 don't have this in the standard library,
# but they can be installed from pip. it's not a big deal if the
# user doesn't have `typing` - they just won't be able to run it
# through mypy.
try:
    from typing import Dict, List, Any, Text, Optional
    Json = Dict[Text, Any]
except ImportError:
    pass

from .user import User
from .channel import Channel
from .emote import Emote

class Message:
    def __init__(self,
                 server,    # type: Any
                 mid,       # type: str
                 author,    # type: User
                 channel,   # type: Channel
                 text,      # type: Text
                 date,      # type: datetime.datetime
                 edit_date, # type: Optional[datetime.datetime]
                 reactions, # type: List[Emote]
                 mentions   # type: List[User]
                ):
        # type: (...) -> None
        self.server = server
        self.mid = mid
        self.author = author
        self.channel = channel
        self.text = text
        self.date = date
        self.edit_date = edit_date
        self.reactions = reactions
        self.mentions = mentions


    @classmethod
    def from_json(cls, server, json):
        # type: (type, Any, Json) -> Message
        mid = json["id"]
        text = json["text"]
        date = datetime.datetime.fromtimestamp(json["date"] / 1000)
        if json["editDate"]:
            edit_date = datetime.datetime.fromtimestamp(json["editDate"]/1000)
        else:
            edit_date = None

        reactions = []
        for i in json["reactions"]:
            reactions.append(Emote.from_json(server, i))

        author_id = json["authorID"]
        author = User.by_id(server, author_id)

        channel_id = json["channelID"]
        channel = Channel.by_id(server, channel_id)

        mentions = []
        for uid in json["mentionedUserIDs"]:
            mentions.append(User.by_id(server, uid))

        return cls(server, mid, author, channel, text, date, edit_date,
                   reactions, mentions)


    def edit(self, newtext):
        # type: (Text) -> None
        "Edits an existing message."
        self.server._request(requests.patch, "messages/" + self.mid,
                             {"text": newtext})
