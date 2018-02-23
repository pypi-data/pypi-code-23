from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import fire
import bcrypt
import os
from . import settings

Base = declarative_base()

file_path = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(file_path, settings.DB_NAME)
# Use for windows pathing only
db_path = "sqlite:///{}".format(db_path)
db_path = db_path.replace('\\', '\\\\')
engine = create_engine(db_path, echo=True)

#
# Use scoped_session for instance usage of database
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
# Sample usage:
# >>> from user_schema_db import db_session, User
# >>> users = db_session.query(User).all()
# >>> users
# >>> []


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    token = Column(String, unique=True)

    def __init__(self, username=None,
                 password=None,
                 token=None):
        self.username = username
        self.password = password
        self.token = token

    def __repr__(self):
        return '<User %r>' % (self.username)



class UserWrapper():
    """For command line usage"""

    def create_db(self):
        Base.metadata.create_all(bind=engine)

    def create_user(self, username, password, token):
        token = str(token).encode()
        hashed = bcrypt.hashpw(token, bcrypt.gensalt())
        user = User(username=username,
                    password=password,
                    token=hashed)
        db_session.add(user)
        db_session.commit()


def main():
    fire.Fire(UserWrapper)


if __name__ == '__main__':
    main()
