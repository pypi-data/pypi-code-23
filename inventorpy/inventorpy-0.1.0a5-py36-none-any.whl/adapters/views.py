from uuid import UUID


class IssueViewBuilder:
    _q = """SELECT description, fk_reporter_uuid, uuid
            FROM issues
            WHERE uuid = :uuid"""

    def __init__(self, db):
        self.db = db

    def fetch(self, uuid):
        session = self.db.get_session()
        result = session.execute(self._q, {'uuid': uuid.bytes})
        record = result.fetchone()
        if record:
            record = read_uuid(record, 'uuid', 'fk_reporter_uuid')
            return dict(record)
        else:
            return None


class IssueListBuilder:
    _q = """SELECT uuid, description, fk_reporter_uuid
            FROM issues"""

    def __init__(self, db):
        self.db = db

    def fetch(self):
        session = self.db.get_session()
        query = session.execute(self._q)
        result = []
        for r in query.fetchall():
            r = read_uuid(r, 'uuid', 'fk_reporter_uuid')
            result.append(r)
        return result


def read_uuid(record, *columns):
    """
    This little helper function converts the binary data
    We store in Sqlite back to a uuid.
    Ordinarily I use postgres, which has a native UniqueID
    type, so this manual unmarshalling isn't necessary
    """
    for column in columns:
        record = dict(record)
        bytes_val = record[column]
        if bytes_val:
            uuid_val = UUID(bytes=bytes_val)
            record[column] = uuid_val
    return record
