import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import and_
from sqlalchemy import func

from extract import Directory, Processed, Template, Pt_Assoc, sync

Base = declarative_base()
Session = sync(Base, os.path.expanduser('~'))
