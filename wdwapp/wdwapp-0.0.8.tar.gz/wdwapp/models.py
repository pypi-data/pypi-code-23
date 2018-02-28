from pyramid.security import Allow, Everyone

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    BigInteger,
    String,
    DateTime,
    Numeric,
    Text,
    Boolean,
    CheckConstraint,
)

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Server(Base):

    "Table of servers who deliver data"

    __tablename__   = 'server'
    
    id              = Column(Integer, primary_key=True,
                        doc="Server unique ID")
    name            = Column(String(20), unique=True,
                        doc="Server unique name")
    url             = Column(Text,
                        doc="URL where to get data")
    long_desc       = Column(Text,
                        doc="Description")
    active          = Column(Boolean,
                        doc="Is this server active (0/1)")


class Sensor(Base):

    "Table of sensors"

    __tablename__   = 'sensor'

    # Identification
    id              = Column(Integer, primary_key=True,
                        doc="Sensor unique ID")
    sid             = Column(Integer, ForeignKey('server.id'),
                        doc="ID of server from where this sensor's data came")
    name            = Column(String(20), unique=True,
                        doc="Sensor unique name")
    short_desc      = Column(String(100),
                        doc="Text displayed in lists, on graphs, etc.")
    long_desc       = Column(Text,
                        doc="Description containing some useful things")
    model           = Column(String(100),
                        doc="Sensor model")
    devid           = Column(String(100),
                        doc="Sensor device ID")
    channel         = Column(Integer,
                        doc="Sensor channel")

    # Operational
    first_seen      = Column(DateTime,
                        doc="Creation time of this sensor")
    last_seen       = Column(DateTime,
                        doc="Last time receiving data from this sensor")
    nbr_seen        = Column(Integer,
                        doc="Number of time receiving data from this sensor")
    new             = Column(Boolean,
                        doc="This sensor has not yet be seen (0/1)")
    cap_bat         = Column(String(100),
                        doc="This sensor give battery level (None or Id string|OK string)")
    bat_low         = Column(Boolean,
                        doc="Battery level LOW (0/1)")

    # Capabilities
    cap_h           = Column(String(100),
                        doc="This sensor can read humidity (None or Id string)")
    cap_t           = Column(String(100),
                        doc="This sensor can read temperature (None or Id string)")
    t_unit          = Column(String(1), CheckConstraint("t_unit in ('c','f','k')"), default='c',
                        doc="Temperature unit of sensor (c=celsius, f=fahrenheit, k=kelvin")
    cap_p           = Column(String(100),
                        doc="This sensor can read pressure (None or Id string)")
    p_unit          = Column(String(1), CheckConstraint("p_unit in ('p','b','m')"), default='p',
                        doc="Pressure unit of sensor (p=hectopascal, b=millibar, m=millimeter of mercury")


class Location(Base):

    "Table of locations"

    __tablename__   = 'location'
    
    id              = Column(Integer, primary_key=True,
                        doc="Location unique ID")
    rank              = Column(Integer, index=True,
                        doc="Sort rank")
    name            = Column(String(20), unique=True,
                        doc="Location unique name")
    short_desc      = Column(String(100),
                        doc="Text displayed in lists, on graphs, etc.")
    long_desc       = Column(Text,
                        doc="Description containing some useful things")
    sid             = Column(Integer, ForeignKey('sensor.id'),
                        unique=True,
                        doc="ID of sensor attached to this location")
    t_min           = Column(Numeric(5, 2),
                        doc="Temperature below which alarm is triggered (or None)")
    t_max           = Column(Numeric(5, 2),
                        doc="Temperature above which alarm is triggered (or None)")
    on_graph        = Column(Boolean,
                        doc="Is this location on graph (0/1)")
    gr_color        = Column(String(6),
                        doc="Color on graph")
    active          = Column(Boolean,
                        doc="Is this location active (0/1)")


class WeatherData(Base):

    "Table of weather data incoming from sensors"

    __tablename__   = 'weather_data'
    
    timestp         = Column(DateTime, primary_key=True,
                        doc="Date time of reading")
    lid             = Column(Integer, ForeignKey('location.id'),
                        primary_key=True,
                        doc="ID in location table")
    temperature     = Column(Numeric(5, 2),
                        doc="Temperature been read")
    humidity        = Column(Integer,
                        doc="Humidity been read")
    pressure        = Column(Numeric(5, 2),
                        doc="Pressure been read")
    t_dew           = Column(Numeric(5, 2),
                        doc="Dew point calculated from temp & humidity")
    t_feel          = Column(Numeric(5, 2),
                        doc="feels like temp. calculated from temp. & humidity")


class Compute(Base):

    "Table of temporary weather data used to compute average values"

    __tablename__   = 'compute'
    
    lid             = Column(Integer, ForeignKey('location.id'),
                        primary_key=True,
                        doc="ID in location table")
    start           = Column(BigInteger,
                        doc="Timestanp of first reading")
    last            = Column(BigInteger,
                        doc="Timestanp of last reading")
    t_sum           = Column(Numeric(10, 2),
                        doc="Summation of temperature since start")
    t_count         = Column(Integer,
                        doc="Number of temperature since start")
    h_sum           = Column(Numeric(10, 2),
                        doc="Summation of humidity since start")
    h_count         = Column(Integer,
                        doc="Number of humidity since start")
    p_sum           = Column(Integer,
                        doc="Summation of pressure since start")
    p_count         = Column(Integer,
                        doc="Number of pressure since start")
    t_min           = Column(Boolean,
                        doc="Minimal temp alarm is triggered")
    t_max           = Column(Boolean,
                        doc="Maximal temp alarm is triggered")


class ToIgnore(Base):

    """Table of sensors to ignore
        Data that match all keys/value with same gid are ignored.
    """

    __tablename__   = 'to_ignore'

    # Identification
    id              = Column(Integer, primary_key=True,
                        doc="Sensor unique ID")
    gid             = Column(Integer, index=True,
                        doc="Sensor ignore group ID")
    key             = Column(String(100),
                        doc="Key to match")
    value           = Column(String(100),
                        doc="Value to match")

class SensorData(Base):

    """New sensor Data
        Store unrecognized data (to purge regularly)
        Can be used, for example, to reload data from new sensor after
        it is activated or associated to a location.
    """

    __tablename__   = 'sensor_data'
    
    id              = Column(Integer, primary_key=True,
                        doc="Location unique ID")
    sid             = Column(Integer, ForeignKey('sensor.id'),
                        index=True,
                        doc="ID of sensor attached to this location")
    timestp         = Column(DateTime, index=True,
                        doc="Date time of reading")
    data            = Column(Text,
                        doc="Data as read from sensor")


class Root(object):
    __acl__ = [(Allow, Everyone, 'view'),
                (Allow, 'group:editors', 'edit')]

    def __init__(self, request):
        pass
