import os
import json
import logging
import transaction

from datetime import datetime
from edw.logger.util import get_user_data
from edw.logger.decorators import log_errors

EDW_LOGGER_DB = os.environ.get(
    "EDW_LOGGER_DB", "true").lower() in ('true', 'yes', 'on')

logger = logging.getLogger("edw.logger")


def __after_conn_close(user_data, url):

    @log_errors("Cannot log transaction commit.")
    def on_close():
        action = getattr(url, 'split', lambda sep: [''])('/')[-1]
        logger.info(json.dumps({
            "IP": user_data['ip'],
            "User": user_data['user'],
            "Date": datetime.now().isoformat(),
            "URL": url,
            "Action": action,
            "Type": 'Commit',
            "LoggerName": logger.name,
        }))

    return on_close


@log_errors("Cannot log transaction commit.")
def handler_commit(event):
    """ Handle ZPublisher.pubevents.PubBeforeCommit.
        This is the only event where we can intercept a
        transaction before it gets committed. Also the only
        event where hooks can be placed and ensure they are
        only executed after a true DB commit.
    """
    if not EDW_LOGGER_DB:
        return

    # get the active transaction
    txn = transaction.get()

    # get needed values now as the request contents will
    # change after commit.
    user_data = get_user_data(event.request)
    url = event.request.URL

    # transactions that will do a commit have a ZODB.Connection
    # objects in ``_resources``. Since the transaction has an
    # open connection we know it will be committed.
    for conn in txn._resources:
        # ZODB.Connection objects support callbacks on close.
        # In this case we wrap the callback in another function
        # so we can also pass in the event.
        conn.onCloseCallback(__after_conn_close(user_data, url))
