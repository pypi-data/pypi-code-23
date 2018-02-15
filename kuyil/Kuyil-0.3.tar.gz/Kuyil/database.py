from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
import logging

from models.base import Base

url = "mysql://root:root@54.153.107.17:3306/kuyil"
# engine = create_engine('mysql://root:root@localhost:3306/mydatabase')
engine = create_engine(url)
# use session_factory() to get a new Session
_SessionFactory = sessionmaker(bind=engine, autocommit=False, autoflush=False)

session = _SessionFactory()

logger = logging.getLogger(__name__)


def session_factory():
    if not database_exists(engine.url):
        logger.debug("created database")
        create_database(engine.url)
    Base.metadata.create_all(engine)
    global session
    if session:
        session.commit()
        return session
    else:
        session = _SessionFactory()
        session.commit()
        return session


def create_url(data):
    try:
        host = data['mysql']['host']
        port = data['mysql']['port']
        username = data['mysql']['user']
        password = data['mysql']['password']
        db = data['mysql']['db']
        mysql_url = 'mysql://' + username + ":" + password + "@" + host + ":" + port + "/" + db
        logger.info("mysql url : " + mysql_url)
        return mysql_url
    except KeyError as error:
        logger.error(error + " key is not found in the config")


def database_init(config):
    global url
    url = create_url(config)
    logger.info("mysql url is updated : " + url)
    global engine
    engine = create_engine(url)
    logger.debug("Engine is udpated")
    global _SessionFactory
    _SessionFactory = sessionmaker(bind=engine, autocommit=False, autoflush=True)
    logger.debug("session factory is updated")
    global session
    session = _SessionFactory()
    logger.debug("session is updated")


def test_init():
    global url
    url = "sqlite:///foo.db"
    logger.info("mysql url is updated : " + url)
    global engine
    engine = create_engine(url)
    logger.debug("Engine is udpated")
    global _SessionFactory
    _SessionFactory = sessionmaker(bind=engine, autocommit=False, autoflush=True)
    logger.debug("session factory is updated")
    global session
    session = _SessionFactory()
    logger.debug("session is updated")