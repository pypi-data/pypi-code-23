from sqlalchemy import Column, INTEGER

from piecash.sa_extra import DeclarativeBase


class B:
    __tablename__ = "b"
    guid = Column(type_=INTEGER,primary_key=True)

    def __init__(self):
        pass

    def __unirepr__(self):
        return "B<>"
