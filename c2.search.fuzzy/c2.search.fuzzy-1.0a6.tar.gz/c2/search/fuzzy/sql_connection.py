
from zope.component.interfaces import ComponentLookupError
from zope.component import getUtility
from sqlalchemy.exc import SQLAlchemyError, ArgumentError, OperationalError
from z3c.saconfig import named_scoped_session
from z3c.saconfig.interfaces import IEngineFactory
from c2.search.fuzzy.words_for_fuzzy_model import Base, Word

DB_CONNECTION_NAME = "c2fuzzysqldb"


def custom_scoped_session(db_name):
    engineFactory = getUtility(IEngineFactory, name=db_name) #, pool_recycle=0)
    # engineFactory.kw['pool_recycle'] = 0
    # # import pdb;pdb.set_trace()
    # print "engineFactory.configuration: ", engineFactory.configuration() #TODO: cheking
    # print "engineFactory.kw: ", engineFactory.kw
    return named_scoped_session(db_name)



def get_db_status(db_name):
    try:
        Session = custom_scoped_session(db_name)
        session = Session()
    except ComponentLookupError:
        return (False, False, "No DB session")
    except ArgumentError:
        return (False, False, "Wrong DB URI")
    try:
        word_first = session.query(Word).first()
    except SQLAlchemyError:
        return (True, False, "No DB table")
    return (True, session, "Created")


def create_db_table(db_name):
    Session = custom_scoped_session(db_name)
    session = Session()
    try:
        Base.metadata.create_all(session.bind)
    except OperationalError:
        return False
    else:
        return True