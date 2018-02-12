
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

from base import Table


class CommunityType(Table, table_name='communit_types'):
    id = Column(Serial, primary_key=True, unique=True)

    name = Column(Text, nullable=False)


class Community(Table, table_name='communities'):
    id = Column(Serial, primary_key=True, unique=True)

    type = Column.with_name('type_id', Integer, foreign_key=ForeignKey(CommunityType.id))

    identifier = Column(String, nullable=False)
    name = Column(Text, nullable=False)

    status = Column(Integer)

    image = Column(String, nullable=False)
    lat = Column(Numeric(8, 12), nullable=False)
    lon = Column(Numeric(8, 12), nullable=False)
    size = Column(Integer, nullable=False)

    created = Column(Timestamp)
    updated = Column.with_name('modified', Timestamp)


class DiscordMeta(Table, table_name='community_discord_meta'):
    id = Column(Serial, primary_key=True, unique=True)

    community = Column.with_name('community_id', Integer, foreign_key=ForeignKey(Community.id))

    admin_count = Column(Integer, nullable=False)
    user_count = Column(Integer, nullable=False)
    online_count = Column(Integer, nullable=False)

    valor = Column(Boolean, nullable=False, default=True)
    mystic = Column(Boolean, nullable=False, default=True)
    instinct = Column(Boolean, nullable=False, default=True)

    min_player_level = Column(SmallInt, nullable=False, default=0)
    registrations = Column(SmallInt, nullable=False, default=0)
    scanners = Column.with_name('has_scanners', Boolean, nullable=False, default=0)

    server = Column(Text, nullable=False)
    channel = Column(BigInt)

    updated = Column(Timestamp)
