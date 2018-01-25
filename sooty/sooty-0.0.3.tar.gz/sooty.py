from __future__ import print_function
from contextlib import contextmanager
from datetime import datetime
import os
try:
    from urllib import parse as urlparse
except ImportError:
    import urlparse

from docopt import docopt
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL')
MIGRATION_DIR = "./migrations"


@contextmanager
def create_cursor(db_url):
    con = None
    try:
        con = psycopg2.connect(**parse_postgres_url(db_url))
        cursor = con.cursor()
        yield cursor
        con.commit()
    finally:
        if con is not None:
            con.close()


def parse_postgres_url(url):
    result = urlparse.urlparse(url)
    return {
        'user': result.username,
        'password': result.password,
        'database': result.path[1:],
        'host': result.hostname
    }


def create_migration(name, migration_dir=None):
    migration_dir = migration_dir or MIGRATION_DIR
    if not migration_dir:
        raise ValueError('You must provide a migration_dir.')

    if not os.path.exists(migration_dir):
        os.mkdir(migration_dir)

    file_name = "_".join(p for p in name.split(" ") if p) + \
        "_" + datetime.now().strftime("%Y%m%d%H%M%S") + ".sql"
    full_path = os.path.join(migration_dir, file_name)
    with open(full_path, "w") as f:
        f.write("-- Just type some SQL!\n")
        f.write("-- ALTER TABLE products ADD COLUMN customer_code varchar(11)\n")
        f.close()
    return full_path


class Migration(object):

    def __init__(self, filepath):
        self.filepath = filepath
        self.version = self.filepath.rsplit("_", 1)[1].split(".sql")[0]
        with open(self.filepath) as f:
            self.sql = f.read()

    def __repr__(self):
        return '<Migration {} path:{}'.format(self.version, self.filepath)


class Connection(object):
    """Connection to DB."""

    def __init__(self, db_url=None, migration_dir=None):
        self.migration_dir = migration_dir or MIGRATION_DIR
        self.db_url = db_url or DATABASE_URL

        if not self.db_url:
            raise ValueError("You must provide a db_url.")

        if not self.migration_dir:
            raise ValueError("You must provide a migration_dir.")

    def run(self):
        self.ensure_schema_table()
        results = self.query("select version from schema_info")
        applied = [r[0] for r in results]

        for migration in self.sorted_migrations():
            if migration.version not in applied:
                print("Applying %s" % migration.filepath)
                self.execute(migration.sql)
                self.execute(
                    "INSERT INTO schema_info (version) VALUES ('%s')" % migration.version)
            else:
                print("Skipping %s" % migration.filepath)

    def sorted_migrations(self):
        full_paths = [os.path.join(self.migration_dir, f) for f in os.listdir(self.migration_dir)
                      if f.endswith('.sql')]
        migrations = [Migration(f) for f in full_paths]
        return sorted(migrations, key=lambda m: m.version)

    def ensure_schema_table(self):
        try:
            self.query("select * from schema_info")
        except:
            self.execute("CREATE TABLE schema_info (version varchar(15))")

    def execute(self, statement):
        with create_cursor(self.db_url) as cursor:
            cursor.execute(statement)

    def query(self, query):
        with create_cursor(self.db_url) as cursor:
            results = []
            cursor.execute(query)
            while True:
                rec = cursor.fetchone()
                if rec:
                    results.append(rec)
                else:
                    break
            return results


def cli():
    cli_docs = """Sooty: Simple database migrator.
Usage:
  sooty <action> [<params>...] [--url=<url>] [--dir=<dir>]
  sooty (-h | --help)
Options:
  -h --help     Show this screen.
  --url=<url>   The database URL to use. Defaults to $DATABASE_URL.
  --dir=<dir>   The directory containing migrations. Defaults to ./migrations/
Supported Actions:
   create: creates a new migration file in <dir> using the remaining command line arguments.
           For example: sooty create add product id to invoices
           This would create a file in <dir> named add_product_id_to_invoices_20160218_223015.sql
           where 20160218_223015 is the current time.
   run:    runs migrations in <dir>
Notes:
  - While you may specify a database connection string with --url, sooty
    will automatically default to the value of $DATABASE_URL, if available.
    """
    supported_actions = 'create run'.split()

    # Parse the command-line arguments.
    arguments = docopt(cli_docs)

    action = arguments['<action>']
    params = arguments['<params>']

    if action not in supported_actions:
        print("Action must be one of %s" % ", ".join(supported_actions))
        exit(64)

    if action == 'create':
        if not params:
            print("You must provide a name for your migration")
            exit(66)
        name = " ".join(params)
        result_path = create_migration(name, arguments['--dir'])
        print("Created %s" % result_path)
    elif action == 'run':
        db = Connection(arguments['--url'])
        db.run()

# Run the CLI when executed directly.
if __name__ == '__main__':
    cli()
