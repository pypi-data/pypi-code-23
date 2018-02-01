import sys
import time
import os

from modislock_monitor.tasks import app
from modislock_monitor.config import load_config

# Database
from modislock_monitor.database import Database
from sqlalchemy import text

# Inserts module path into system search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

config = load_config()


def testdb(db):
    """Tests if database connection is valid

    :param Database db: database session
    :return bool: connection succeeded or failed
    """
    try:
        db.session.query("1").from_statement(text("SELECT 1")).all()
        return True
    except:
        return False


def main():
    log_level = 'DEBUG' if config.DEBUG else 'INFO'

    with Database() as db:
        iterations = 0

        while testdb(db) is not True:
            time.sleep(2)
            iterations += 1

            if iterations > 20:
                sys.exit(1)

    argv = [
        'worker',
        '--loglevel=' + log_level,
        '--beat',
        '--purge'
    ]
    app.worker_main(argv)


if __name__ == '__main__':
    main()

