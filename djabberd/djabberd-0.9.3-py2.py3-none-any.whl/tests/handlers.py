# Test handlers


TEST_ARCHIVE = {"username": "USERNAME1", "peer": "USERNAME2",
                "xml": "MESSAGE_STANZA", "body": "TEXT",
                "timestamp": "TIMESTAMP", "direction": "DIRECTION"}
TEST_ARCHIVE_GET = {"archive": [{"username": "USERNAME1", "peer": "USERNAME2",
                                 "xml": "MESSAGE_STANZA", "body": "TEXT",
                                 "timestamp": "TIMESTAMP",
                                 "direction": "DIRECTION"}], "count": 1}
TEST_ROSTER = {"roster": [{"username": "CONTACT", "subscription": "both",
                           "nick": "NICK"}]}


def user_authentication(username, password):
    result = eval(username)
    return result


def user_exists(username):
    result = eval(username)
    return result


def retrieve_user_roster(username):
    user = eval(username)
    if user:
        return TEST_ROSTER


def archive_store(payload):
    pass


def archive_get(username, peer=None, after=None, before=None, limit=None, type=None):
    return TEST_ARCHIVE_GET
