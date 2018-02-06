from uuid import UUID


class IssueViewBuilder:
    _q = """SELECT description, reporter_email, reporter_name
            FROM issues
            WHERE issue_id = :id"""

    def __init__(self, db):
        self.db = db

    def fetch(self, uuid):
        session = self.db.get_session()
        result = session.execute(self._q, {'id': uuid.bytes})
        record = result.fetchone()
        return dict(record)


class IssueListBuilder:
    _q = """SELECT issue_id, description, reporter_email, reporter_name
            FROM issues"""

    def __init__(self, db):
        self.db = db

    def fetch(self):
        session = self.db.get_session()
        query = session.execute(
            'SELECT issue_id, description, reporter_email, reporter_name ' +
            ' FROM issues')
        result = []
        for r in query.fetchall():
            r = read_uuid(r, 'issue_id')
            result.append(r)
        return result


def read_uuid(record, column):
    """
    This little helper function converts the binary data
    We store in Sqlite back to a uuid.
    Ordinarily I use postgres, which has a native UniqueID
    type, so this manual unmarshalling isn't necessary
    """
    record = dict(record)
    bytes_val = record[column]
    uuid_val = UUID(bytes=bytes_val)
    record[column] = str(uuid_val)
    return record
