from datetime import datetime

from eryx_deploy.assets.machines.with_shell.abs_with_shell import MachineWithShell
from eryx_deploy.utils.date_utils import today_datetime, DATE_TIME_FORMAT
from eryx_deploy.utils.interactive_console import InteractiveConsole


class UbuntuMachine(MachineWithShell):
    def __init__(self, hostname, ssh_connection, project_path, is_local):
        super(UbuntuMachine, self).__init__(hostname=hostname, project_path=project_path, ssh_connection=ssh_connection,
                                            is_local=is_local)
        self._apt_updated = False

    # operations

    def create_project_folder(self):
        self.run('sudo mkdir -p %s' % self._project_path)
        self.run('sudo chown $USER %s' % self._project_path)

    # machine protocol - installs

    def install_git(self):
        self._update_apt()
        self.run('sudo apt-get install git-core -y')

    def install_basic_platform_build_tools(self):
        self._update_apt()
        self.run('sudo apt-get install build-essential -y')

    def install_postgresql_client(self, version='9.5'):
        self._update_apt()
        self.run('sudo apt-get install libpq-dev postgresql-client-%s -y' % version)

    def install_postgresql_server(self, master_username, master_password):
        self._update_apt()
        self.run('sudo apt-get install postgresql -y')

        if not self._postgresql_server_already_configured(master_username):
            self._initial_postgresql_server_config(master_username, master_password)

    def install_mysql_client(self):
        raise NotImplementedError("Not implemented yet! Please do it :)")

    def install_mysql_server(self):
        raise NotImplementedError("Not implemented yet! Please do it :)")

    def install_nginx(self):
        self._update_apt()
        self.run('sudo apt-get install nginx -y')

    def install_supervisor(self):
        self._update_apt()
        self.run('sudo apt-get install supervisor -y')

    def install_nodejs(self, version='7'):
        if version == self.nodejs_version(major_only=True):
            return

        self._update_apt()
        self.install_basic_platform_build_tools()

        download_url = 'https://deb.nodesource.com/setup_%s.x' % version
        self.run('curl -sL %s -o nodesource_setup.sh' % download_url)
        self.run('sudo bash nodesource_setup.sh')

        self.run('sudo apt-get install nodejs -y')

    def install_yarn(self):
        if self.yarn_version() is not None:
            return

        self.install_nodejs()

        self._add_apt_repository("yarn", configline="deb https://dl.yarnpkg.com/debian/ stable main",
                                 keyurl="https://dl.yarnpkg.com/debian/pubkey.gpg")
        self.run('sudo apt-get install yarn -y')

    def install_python_lib(self, major_version=2):
        self._update_apt()
        if major_version == 2:
            self.run('sudo apt-get install python-pip python-dev -y')
        if major_version == 3:
            self.run('sudo apt-get install python3-pip python3-dev -y')
        if major_version != 2 and major_version != 3:
            InteractiveConsole.abort("Unsupported python version! Only version 2 or 3 are supported on this machine.")

    def install_ruby(self):
        self._update_apt()
        self.run('sudo apt-get install ruby-full -y')

    def install_rbenv(self):
        self._update_apt()
        self.install_git()

        if self.path_exists('.rbenv'):
            InteractiveConsole.show_info("Rbenv already installed, skipping installation.")
            return

        self.run('git clone git://github.com/sstephenson/rbenv.git .rbenv')
        self.run('echo \'export PATH="$HOME/.rbenv/bin:$PATH"\' >> ~/.bash_profile')
        self.run('echo \'eval "$(rbenv init -)"\' >> ~/.bash_profile')

        self.run('git clone git://github.com/sstephenson/ruby-build.git ~/.rbenv/plugins/ruby-build')
        self.run('echo \'export PATH="$HOME/.rbenv/plugins/ruby-build/bin:$PATH"\' >> ~/.bash_profile')
        # self.run('source ~/.bash_profile')

    def install_sass(self):
        self.install_ruby()
        self.run('sudo gem install sass')

    def install_ruby_compile_depedencies(self):
        self.install_basic_platform_build_tools()
        self.run('sudo apt-get install libssl-dev libreadline-dev zlib1g-dev -y')

    # utility commands

    def current_user(self):
        return self.run('whoami')

    def command_path(self, command):
        whereis_output = self.run('whereis %s' % command)
        return whereis_output[len(command) + 2:]  # output: 'command: /path/to/command'

    # private - bootstrapping configs

    def _postgresql_server_already_configured(self, master_username):
        with self.cd('~postgres'):
            res = self.run_check('''sudo -u postgres psql -t -A -c "SELECT COUNT(*) FROM pg_user WHERE usename 
                = '%(name)s';"''' % {'name': master_username},
                                 message="Checking if PostgreSQL user '%s' exists ..." % master_username)
            return res == "1"

    def _initial_postgresql_server_config(self, master_username, master_password):
        with self.cd('~postgres'):
            self.run(
                '''sudo -u postgres psql -c "CREATE USER %(name)s SUPERUSER NOCREATEDB NOCREATEROLE INHERIT LOGIN 
                ENCRYPTED PASSWORD '%(password)s';"''' % {'name': master_username, 'password': master_password})

    # machine-protocol - get package versions (or None if not installed)

    def nodejs_version(self, major_only=False):
        """
        Get the version of Node.js currently installed.

        Returns ``None`` if it is not installed.
        """
        res = self.run_check('nodejs --version', message="Checking nodejs installed version...")

        if res.failed:
            return None
        else:
            if major_only:
                return res[1]
            else:
                return res[1:]

    def yarn_version(self):
        """
        Get the version of Yarn currently installed.

        Returns ``None`` if it is not installed.
        """
        res = self.run_check('yarn -v', message="Checking yarn installed version...")

        if res.failed:
            return None
        else:
            return res

    # manage db dump files on server

    def create_db_dump_of(self, database):
        dump_file_path = '~/%s+%s.gz' % (database.name(), today_datetime())
        database.dump(dump_output_path=dump_file_path)

        return dump_file_path

    def exists_a_db_dump_from_today(self, database_name):
        last_backup_date_time = self.latest_db_dump_datetime(database_name)
        if last_backup_date_time:
            return last_backup_date_time.date() == datetime.today().date()
        return False

    def latest_db_dump_datetime(self, database_name):
        date_times = []

        file_names = self._list_dir('~')

        for file_name in file_names:
            try:
                db_name = file_name.split('+')[0]
                date_time = file_name.split('+')[-1].split('.gz')[0]
                date_time = datetime.strptime(date_time, DATE_TIME_FORMAT)

                if db_name == database_name:
                    date_times.append(date_time)
            except ValueError:
                pass

        if len(date_times):
            return max(date_times)

    def latest_db_dump_filename(self, database_name):
        last_date_time = self.latest_db_dump_datetime(database_name)
        return '%s+%s.gz' % (database_name, last_date_time.strftime(DATE_TIME_FORMAT))

    # private

    def _update_apt(self):
        if not self._apt_updated:
            self.run('sudo apt-get update -y')
            self._apt_updated = True

    def _add_apt_repository(self, name, configline, keyurl):
        self.run('curl -sS %s | sudo apt-key add -' % keyurl)
        self.run('echo "%s" | sudo tee /etc/apt/sources.list.d/%s.list' % (configline, name))
        self._apt_updated = False
        self._update_apt()

    def _list_dir(self, dir_path):
        if dir_path[-1] != '/':
            dir_path += '/'

        file_names = self.run("ls -m %s" % dir_path)
        file_names = map(lambda s: s.strip(), file_names.split(","))
        return file_names
