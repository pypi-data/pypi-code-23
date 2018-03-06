import importlib
import threading
import configparser
import pathlib
import pickle
import os

from ScopusWp.database import MySQLDatabaseAccess
from ScopusWp.config import PATH

# THE TEMPLATES FOR THE NON CODE FILES

CONFIG_INI_TEMPLATE = (
    '[SCOPUS]\n'
    'api-key = # YOUR API KEY'
    'url = https://api.elsevier.com/content\n'
    '\n'
    '[KITOPEN]\n'
    'url = https://publikationen.bibliothek.kit.edu/publikationslisten\n'
    '\n'
    '[WORDPRESS]\n'
    'url = # THE URL TO YOUR WP XMLRPC.PHP\n'
    'username = # YOUR WP USER\n'
    'password = # YOUR WP PASSWORD\n'
    'update_expiration = # AMOUNT OF DAYS BETWEEN UPDATES'
    '\n'
    '[MYSQL]\n'
    'host = localhost\n'
    'database = # YOUR MYSQL DATABASE NAME'
    'username = # YOUR MYSQL USER'
    'password = # YOUR PASSWORD'
    '\n'
    '[LOGGING]\n'
    'folder = logs\n'
    'debug_log_name = log\n'
    'activity_log_name = log\n'
)

AUTHORS_INI_TEMPLATE = (
    '[SHORTHAND]\n'
    'ids = [] # LIST OF SCOPUS IDS ASSOCIATED WITH AUTHOR\n'
    'first_name = # FIRST NAME\n'
    'last_name = # LAST NAME\n'
    'keywords = [] # WORDPRESS CATEGORIES TO ASSOCIATE AUTHOR PUBLICATIONS WITH\n'
    'scopus_whitelist = [] # SCOPUS AFFILIATION IDS TO ACCEPT\n'
    'scopus_blacklist = [] # SCOPUS AFFILIATION IDS TO IGNORE\n'
    '\n'
    '# You can add more authors by appending sections like the template above\n'
)

ID_JSON_TEMPLATE = (
    '{\n'
    '"counter": 0,\n'
    '"used": [],\n'
    '"unused": []\n'
    '}\n'
)

# THE SQL SCRIPTS NEEDED FOR THE SETUP

REFERENCE_SQL = (
    'CREATE TABLE reference '
    '('
    'id BIGINT PRIMARY KEY,'
    'wordpress_id BIGINT,'
    'scopus_id BIGINT,'
    'comments_updated_datetime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'
    ') ENGINE INNODB;'
    'CREATE UNIQUE INDEX reference_id_uindex ON reference (id);'
    'COMMIT;'
)

COMMENT_REFERENCE_SQL = (
    'CREATE TABLE comment_reference'
    '('
    'internal_id BIGINT PRIMARY KEY,'
    'wordpress_post_id BIGINT,'
    'wordpress_comment_id BIGINT,'
    'scopus_id BIGINT'
    ') ENGINE INNODB;'
    'CREATE UNIQUE INDEX comment_reference_inernal_id_uindex ON comment_reference (internal_id);'
    'COMMIT;'
)

PUBLICATIONS_SQL = (
    'CREATE TABLE publications ('
    'scopus_id BIGINT PRIMARY KEY NOT NULL,'
    'eid VARCHAR(64),'
    'doi VARCHAR(64),'
    'creator TEXT,'
    'description LONGTEXT,'
    'journal TEXT,'
    'volume VARCHAR(64),'
    'date VARCHAR(64),'
    'authors LONGTEXT,'
    'keywords TEXT,'
    'citations TEXT'
    ') ENGINE INNODB;'
    'CREATE UNIQUE INDEX publications_scopus_id_uindex ON publications (scopus_id);'
    'CREATE UNIQUE INDEX publications_eid_uindex ON publications (eid);'
    'CREATE UNIQUE INDEX publications_doi_unidex ON publications (doi);'
    'COMMIT;'
)

PUBLICATION_CACHE_SQL = (
    'CREATE TABLE publication_cache ('
    'scopus_id BIGINT PRIMARY KEY NOT NULL,'
    'eid VARCHAR(64),'
    'doi VARCHAR(64),'
    'creator TEXT,'
    'description LONGTEXT,'
    'journal TEXT,'
    'volume VARCHAR(64),'
    'date VARCHAR(64),'
    'authors LONGTEXT,'
    'keywords TEXT,'
    'citations TEXT'
    ') ENGINE INNODB;'
    'CREATE UNIQUE INDEX publications_scopus_id_uindex ON publications (scopus_id);'
    'CREATE UNIQUE INDEX publications_eid_uindex ON publications (eid);'
    'CREATE UNIQUE INDEX publications_doi_unidex ON publications (doi);'
    'COMMIT;'
)

AUTHOR_CACHE_SQL = (
    'CREATE TABLE author_cache ('
    'author_id BIGINT PRIMARY KEY NOT NULL,'
    'first_name TEXT,'
    'last_name TEXT,'
    'h_index INT,'
    'citation_count INT,'
    'document_count INT,'
    'publications TEXT'
    ') ENGINE INNODB;'
    'CREATE UNIQUE INDEX author_cache_author_id_uindex ON author_cache (author_id);'
    'COMMIT;'
)


class ProjectPathInputController:

    def __init__(self):
        self._path = None

    @property
    def path(self):
        self.run()
        return self._path

    def run(self):
        if not self.check_config():
            self.prompt_path()

    def prompt_path(self):
        while True:
            inp = input('\nENTER PROJECT PATH: ')
            try:
                path = pathlib.Path(inp)
                if path.exists() and path.is_dir():
                    self._path = str(path)
                else:
                    print('INVALID PATH, TRY AGAIN')
                    continue
            except:
                print('INVALID INPUT, TRY AGAIN')
                continue

    def check_config(self):
        import IndicoWp.config as _config
        # In case the project path value is not empty, it is save to assume it has been set already and the path is
        # still valid
        if _config.PATH == '':
            print('NO PATH HAS BEEN SET')
            return False

        # Asking the user if he wants to keep that path or change it
        print('CURRENT PATH:\n{}'.format(_config.PATH))
        inp = input('\nDo you want to keep that path? Type "N" to change...')
        if inp.lower() == 'n' or inp.lower() == 'no':
            return False
        else:
            return True


class FolderSetupController:

    def __init__(self, project_path):
        self.path = project_path

        self.logs_path = pathlib.Path(self.path + '/logs')

        self.temp_path = pathlib.Path(self.path + '/temp')

    def run(self):
        if not self.logs_exists():
            self.create_logs_folder()
            print('created the logs folder')
        else:
            print('Logs folder already exists')

        if not self.temp_exists():
            self.create_temp_folder()
            print('created the temp folder')
        else:
            print('temp folder already exists')

    def create_logs_folder(self):
        self.logs_path.mkdir()

    def create_temp_folder(self):
        self.temp_path.mkdir()

    def logs_exists(self):
        return self.logs_path.exists() and self.logs_path.is_dir()

    def temp_exists(self):
        return self.temp_path.exists() and self.temp_path.is_dir()


class ConfigSetupController:

    def __init__(self, project_path):
        self.path = project_path

        self.config_path = pathlib.Path(self.path) / 'config.ini'

    def run(self):
        if not self.exists():
            self.create()
            print('\nCREATED CONFIG.INI')
        else:
            print('\nCONFIG FILE ALREADY EXISTS. KEEPING THE EXISTING FILE')

    def create(self):
        with self.config_path.open(mode='w+') as file:
            file.write(CONFIG_INI_TEMPLATE)
            file.flush()

    def exists(self):
        return self.config_path.exists() and self.config_path.is_file()


class IdsJsonSetupController:

    def __init__(self, project_path):
        self.path = project_path

        self.ids_path = pathlib.Path(self.path) / 'ids.json'

    def run(self):
        if not self.exists():
            self.create()
            print('\nCREATED IDS.JSON')
        else:
            print('\nIDS.JSON ALREADY EXISTS. KEEPING THE EXISTING FILE')

    def create(self):
        with self.ids_path.open(mode='w+') as file:
            file.write(ID_JSON_TEMPLATE)
            file.flush()

    def exists(self):
        return self.ids_path.exists() and self.ids_path.is_file()


class ObservedAuthorsSetupController:

    def __init__(self, project_path):
        self.project_path = project_path

        self.path = pathlib.Path(self.project_path) / 'authors.ini'

    def run(self):
        if not self.exists():
            self.create()

    def exists(self):
        return self.path.exists() and self.authors_path.is_file()

    def create(self):
        with self.path.open(mode='w+') as file:
            file.write(AUTHORS_INI_TEMPLATE)


class SQLSetupController:

    def __init__(self):
        self.access = MySQLDatabaseAccess()

    def run(self):
        if not self.database_exists('publication_cache'):
            self.access.execute(PUBLICATION_CACHE_SQL)

        if not self.database_exists('publications'):
            self.access.execute(PUBLICATIONS_SQL)

        if not self.database_exists('author_cache'):
            self.access.execute(AUTHOR_CACHE_SQL)

        if not self.database_exists('reference'):
            self.access.execute(REFERENCE_SQL)

        if not self.database_exists('comment_reference'):
            self.access.execute(COMMENT_REFERENCE_SQL)

    def database_exists(self, database_name):
        try:
            sql = (
                'SELECT * FROM {database};'
            ).format(database=database_name)
            self.access.execute(sql)
            return True
        except:
            return False


class SetupController:

    def __init__(self):
        # Getting the path to the project folder
        self.path_input_controller = ProjectPathInputController()
        self.project_path = self.path_input_controller.path

        self.folder_setup_controller = FolderSetupController(self.project_path)
        self.ids_setup_controller = IdsJsonSetupController(self.project_path)
        self.config_setup_controller = ConfigSetupController(self.project_path)
        self.observed_author_setup_controller = ObservedAuthorsSetupController(self.project_path)

    def setup_files(self):
        # Setting up all the folders
        self.folder_setup_controller.run()

        # Setting up the data files
        self.config_setup_controller.run()
        self.ids_setup_controller.run()
        self.observed_author_setup_controller.run()

    def setup_database(self):
        pass
