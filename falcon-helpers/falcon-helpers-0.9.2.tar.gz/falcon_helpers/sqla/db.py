import sqlalchemy as sa

_session_maker = sa.orm.sessionmaker()
session = sa.orm.scoped_session(_session_maker)
