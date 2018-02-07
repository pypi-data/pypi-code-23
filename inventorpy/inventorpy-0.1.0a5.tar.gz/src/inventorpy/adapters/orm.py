from sqlalchemy import (
    Table, Column, MetaData, String, Integer,
    Text, create_engine, event, ForeignKey
)

from sqlalchemy.orm import (
    mapper, scoped_session, sessionmaker,
    relationship
)

from sqlalchemy_utils.functions import create_database, drop_database
from sqlalchemy_utils.types.uuid import UUIDType

from inventorpy.domain.models import Issue, User, Assignment
from inventorpy.domain.ports import (
    UnitOfWork, UnitOfWorkManager, IssueLogPort, UserRepositoryPort
)

from sqlalchemy.exc import ArgumentError


class IssueLog(IssueLogPort):
    def __init__(self, session):
        self._session = session

    def _get(self, uuid):
        issue = self._session.get(uuid)
        return issue or None

    def add(self, issue: Issue) -> None:
        self._session.add(issue)


class UserRepository(UserRepositoryPort):
    def __init__(self, session):
        self._session = session

    def _get(self, uuid):
        user = self._session.query(User).first()
        return user

    def add(self, user: User) -> None:
        self._session.add(user)


class SqlAlchemyUnitOfWorkManager(UnitOfWorkManager):
    """The unit of work manager returns a new unit of work.
    This UOW is backed by an sql alchemy session whose
    lifetime can be scoped to a web request or a long lived
    background job.

    Will create a new session or gives an existing one depending
    on how sql alchemy has been configured
    """

    def __init__(self, session_factory, bus):
        self.session_factory = session_factory
        self.bus = bus

    def start(self):
        return SqlAlchemyUnitOfWork(self.session_factory, self.bus)


class SqlAlchemyUnitOfWork(UnitOfWork):
    """
    The unit of work captures the idea of a set of things that
    need to happen together.

    Usually, in a relational database,
    one unit of work == one database transaction.
    """

    def __init__(self, session_factory, bus):
        self.flushed_events = list()
        self.session_factory = session_factory
        self.bus = bus
        event.listen(self.session_factory, "after_flush",
                     self.gather_events)
        event.listen(self.session_factory, "loaded_as_persistent",
                     self.setup_events)

    def __enter__(self):
        self.session = self.session_factory()
        self.flushed_events = []
        return self

    def __exit__(self, ex, value, traceback):
        self.session.close()
        self.publish_events()

    def commit(self):
        # TODO: need to add some logging and error handling here.
        self.session.flush()
        self.session.commit()

    def rollback(self):
        self.flushed_events = []
        self.session.rollback()

    def setup_events(self, session, entity):
        entity.events = []

    def gather_events(self, session, ctx):
        flushed_objects = [e for e in session.new] + [e for e in session.dirty]
        for e in flushed_objects:
            try:
                self.flushed_events += e.events
            except AttributeError:
                pass

    def publish_events(self):
        for e in self.flushed_events:
            self.bus.handle(e)

    # Repository was placed here for convenience.
    @property
    def issues(self):
        return IssueLog(self.session)

    @property
    def users(self):
        return UserRepository(self.session)


class SqlAlchemy:

    def __init__(self, uri):
        self.metadata = None
        self.bus = None
        self.engine = create_engine(uri)
        self._session_factory = scoped_session(sessionmaker(self.engine))
        try:
            self.configure_mappings()
        except ArgumentError:
            pass

    @property
    def unit_of_work_manager(self):
        return SqlAlchemyUnitOfWorkManager(self._session_factory, self.bus)

    def recreate_schema(self):
        drop_database(self.engine.url)
        self.create_schema()

    def create_schema(self):
        create_database(self.engine.url)
        self.metadata.create_all()

    def get_session(self):
        return self._session_factory()

    def set_message_bus(self, bus):
        self.bus = bus

    def configure_mappings(self):
        """Uses sql alchemy 'classical mapping'.
        """
        self.metadata = MetaData(self.engine)

        User.__composite_values__ = lambda i: (i.first_name, i.email)

        # Create the table metadata separately
        # with the `Table` construct
        issues = Table('issues', self.metadata,
                       Column('pk', Integer, primary_key=True),
                       Column('uuid', UUIDType),
                       Column('fk_reporter_uuid', UUIDType,
                              ForeignKey('users.uuid')),
                       Column('description', Text))

        assignments = Table('assignments', self.metadata,
                            Column('pk', Integer, primary_key=True),
                            Column('uuid', UUIDType),
                            Column('fk_assignment_id', UUIDType,
                                   ForeignKey('issues.uuid')),
                            Column('assigned_by', String(50)),
                            Column('assigned_to', String(50)))

        users = Table('users', self.metadata,
                      Column('pk', Integer, primary_key=True),
                      Column('uuid', UUIDType),
                      Column('first_name', String(50)),
                      Column('last_name', String(50)),
                      Column('email', String(50)),
                      Column('password_hash', String(250)))

        # Then associate the class: Issue
        # to the table metadata
        mapper(Issue, issues,
               properties={
                   '__pk': issues.c.pk,
                   'uuid': issues.c.uuid,
                   'description': issues.c.description,
                   'reporter': relationship(User, backref='user'),
                   '_assignments': relationship(Assignment, backref='issue')})

        mapper(Assignment, assignments,
               properties={
                   '__pk': assignments.c.pk,
                   'uuid': assignments.c.uuid,
                   'assigned_to': assignments.c.assigned_to,
                   'assigned_by': assignments.c.assigned_by})

        mapper(User, users,
               properties={
                   '__pk': users.c.pk,
                   'uuid': users.c.uuid,
                   'first_name': users.c.first_name,
                   'last_name': users.c.last_name,
                   'email': users.c.email,
                   'password_hash': users.c.password_hash})
