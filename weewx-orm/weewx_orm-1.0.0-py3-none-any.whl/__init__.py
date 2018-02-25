from traceback import print_exc

from marshmallow_sqlalchemy import ModelSchema
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists

from .archive_schema import schema as archive_schema_sql


class WeewxDB:
    def __init__(self, database_file):
        '''
        :param database_file: Path to the sqlite database
        '''
        self._database_file = 'sqlite:///' + database_file

        self._engine = create_engine(self._database_file)

        if not database_exists(self._database_file):
            self._init_database()

        self._Base = automap_base()
        self._Base.prepare(self._engine, reflect=True)
        self.session = Session(sessionmaker(bind=self._engine))

        self.tables = self._Base.classes

        class ArchiveSchema(ModelSchema):
            class Meta:
                model = self.tables.archive

        self.archive_schema = ArchiveSchema()

    def archive_query_interval(self, _from, to):
        '''
        :param _from: Start of interval (int) (inclusive)
        :param to: End of interval (int) (exclusive)
        '''
        with self.session as session:
            table = self.tables.archive

            try:
                results = session.query(table)\
                    .filter(table.dateTime >= _from)\
                    .filter(table.dateTime < to)\
                    .all()

                print('Query returned {} items'.format(len(results)))
                return [self.archive_schema.dump(entry).data for entry in results]
            except Exception as e:
                print_exc()
                session.rollback()

    def archive_insert_data(self, data_dump):
        '''
        :param data: Archive table data
        :type data: list[archive]
        '''
        with self.session as session:
            try:
                data = [self.tables.archive(**entry) for entry in data_dump]

                session.add_all(data)
                session.commit()
            except Exception as e:
                print_exc()
                session.rollback()

    def _init_database(self):
        with self._engine.connect() as con:
            con.execute(archive_schema_sql)


class Session:
    def __init__(self, session_maker):
        self._session_maker = session_maker
        self._session = None

    def __enter__(self):
        self._session = self._session_maker()
        return self._session

    def __exit__(self, exc_type, exc_value, traceback):
        self._session.close()
