import os

from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import Column, Integer, String, Unicode, Boolean, Float, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker, scoped_session, relationship

# these imports are for custom SQL constructs
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import DateTime

from sqlalchemy.exc import IntegrityError

# create a custom utcnow function
class utcnow(expression.FunctionElement):
    type = DateTime()


@compiles(utcnow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"

@compiles(utcnow, 'sqlite')
def sqlite_utcnow(element, compiler, **kw):
    return "CURRENT_TIMESTAMP"


class AppMixin(object):
    """
    Provide common attributes to our models
    In this case, lowercase table names, timestamp, and a primary key column
    """

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    __mapper_args__ = {'always_refresh': True}

    id = Column(Integer, primary_key=True)
    # the correct function is automatically selected based on the dialect
    timestamp = Column(DateTime, server_default=utcnow())

Base = declarative_base()


class Directory(Base, AppMixin):
    """ The full path to the directory in which the image extraction has been run """
    fullpath = Column(Unicode(250), nullable=False, unique=True)
    pprocessed = relationship("Processed", back_populates="path")
    def __repr__(self):
        return "%s, %s files processed" % (self.fullpath, len(self.pprocessed))


class Pt_Assoc(Base):
    """ Unique combinations of a Processed file and a Template """
    __tablename__ = 'pt_assoc'
    template_id = Column('template_id', Integer, ForeignKey('template.id'), primary_key=True)
    processed_id = Column('processed_id', Integer, ForeignKey('processed.id'), primary_key=True)
    # was an image successfully extracted?    
    success = Column(Boolean, nullable=False, index=True)
    template = relationship("Template", back_populates="processeds")
    processed = relationship("Processed", back_populates="templates")
    def __repr__(self):
        return "Template: %s, success? %s" % (self.template, self.success)


class Processed(Base, AppMixin):
    """ A processed image. MD5 is the file MD5, not filename MD5 """
    # the file name without a path     
    fname = Column(Unicode(250), nullable=False, unique=True)
    md5 = Column(String(32), nullable=False, unique=True)
    path_id = Column(Integer, ForeignKey('directory.id'))
    path = relationship("Directory", back_populates="pprocessed", uselist=False)
    templates = relationship("Pt_Assoc", back_populates="processed")
    
    @property
    def fullpath(self):
        return os.path.join(self.path.fullpath, self.fname)
    
    def __init__(self, fname, fullpath):
        self.fname = fname
        self.md5 = md5(os.path.join(fullpath, fname))
        self.path = create_or_get_path(fullpath)
    def __repr__(self):
        return "%s, templates: %s" % (self.fname, self.templates)


class Template(Base, AppMixin):
    fname = Column(Unicode(250), nullable=False, unique=True)
    md5 = Column(String(32), nullable=False, unique=True)
    processeds = relationship("Pt_Assoc", back_populates="template", order_by="Pt_Assoc.success")

    def __init__(self, fname, fullpath):
        self.fname = fname.decode()
        self.md5 = md5(os.path.join(fullpath, fname))
    def __repr__(self):
        return "%s (%s)" % (self.fname, self.md5)


def sync(bs, db_path):
    """
    Connect to the DB, return a scoped session factory
    """
    # first, bind to or create the db
    pth = u'sqlite:///%s/image_crop.db'.encode('utf8') % db_path
    engine = create_engine(pth)
    # create the tables by syncing metadata from the models
    # bs is a declarative_base instance
    bs.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
    return Session
