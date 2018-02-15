
from asyncqlio import (
    Column,
    Integer,
    SmallInt,
    BigInt,
    String,
    Text,
    Boolean,
    Timestamp,
    ForeignKey,
    Numeric,
    Serial,
)

from .base import Table


class User(Table, table_name='users'):
    id = Column(Serial, primary_key=True, unique=True)

    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    silph_username = Column.with_name('username', String)
    reddit_username = Column(String)
    game_username = Column.with_name('in_game_username', String)

    ban_level = Column(Integer)

    role = Column(Integer)
    is_in_field_test = Column(Integer)

    created = Column(Timestamp)

    @property
    def name(self):
        return self.game_username or 'Traveler #%x' % self.id

    def payload(self):
        struct = {
            'id': self.id,
            'name': self.username,
            'role': self.role,
            'created': int(self.created.timestamp()),
            'version': 0,
        }

        return struct


class UserLogin(Table, table_name='user_logins'):
    id = Column(Serial, primary_key=True, unique=True)

    user = Column.with_name('user_id', Integer, nullable=False)
    vendor = Column.with_name('vendor_id', Integer, nullable=False)

    username = Column(Text)
    identifier = Column(String)

    created = Column(Timestamp)
    updated = Column.with_name('modified', Timestamp)
