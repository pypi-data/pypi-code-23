import os

from eryx_deploy.app_stacks.abs_app_stack import AppStack
from eryx_deploy.assets.databases.postgresql import PostgresDatabase
from eryx_deploy.assets.frameworks.ruby_on_rails import RubyOnRailsProject
from eryx_deploy.assets.language_environments.ruby.rbenv import Rbenv
from eryx_deploy.assets.package_managers.frontend.yarn import Yarn
from eryx_deploy.assets.vcs.git import Git
from eryx_deploy.assets.webservers.ruby.nginx_with_puma import NginxWithPumaWebserver


class RubyOnRailsStack(AppStack):
    """
    Ruby on Rails Stack.
    """

    def __init__(self, host, project_name,
                 remote_url,
                 db_name, db_user, db_password,
                 db=PostgresDatabase, db_port='', db_client=None, db_server=None,
                 ruby_environment=Rbenv,
                 rails_env='production',
                 ruby_webserver=NginxWithPumaWebserver,
                 frontend_package_manager=Yarn,
                 vcs=Git):
        """
        @param host: Machine where project will be deployed. Required.
        @param project_name: Project name that will be used for all configurations. Required.
        @param remote_url: You VCS repo url, like git@gitlab.com:eryx/myproject.git. Required.
        @param db_name: Database name. Required.
        @param db_user: Database user. Required.
        @param db_password: Database user's password. Required.
        @param db: Database class. Check assets/databases for options. Default: PostgresDatabase.
        @param db_port: Database port. Default: ''.
        @param db_client: Database client machine. Default: Host machine.
        @param db_server: Dabatase server machine. Default: Host machine.
        @param ruby_environment: Environment tool where the ruby runtime is going to be installed. Default: Rbenv.
        @param rails_env: Value of RAILS_ENV env variable when doing deployment.
        @param db_server: Dabatase server machine. Default: Host machine.
        @param ruby_webserver: Webserver class. Check assets/webservers/ruby for options.
            Default: NgnixWithPumaWebserver.
        @param vcs: VCS class. Default: Git.
        @param frontend_package_manager: FrontendPackageManager subclass. Check assets/package_manager/frontend
        for options. Default: NullPackageManager (does nothing).
        """

        self._host_machine = host

        if db_client is None:
            db_client = self._host_machine

        if db_server is None:
            db_server = self._host_machine

        self._db = db(client_machine=db_client, server_machine=db_server, name=db_name, port=db_port, user=db_user,
                      password=db_password)

        self._ruby_environment = ruby_environment(host_machine=self._host_machine, ruby_version='2.3.4')

        self._ruby_environment.set_env_var('RAILS_ENV', rails_env)

        self._vcs = vcs(client_machine=host, remote_url=remote_url)

        self._rails_project = RubyOnRailsProject(host_machine=self._host_machine,
                                                 project_name=project_name,
                                                 db=self._db,
                                                 frontend_package_manager=frontend_package_manager,
                                                 ruby_environment=self._ruby_environment)

        self._ruby_webserver = ruby_webserver(machine=host, webapp_name=project_name,
                                              ruby_environment=self._ruby_environment)

    def host_machine(self):
        return self._host_machine

    def db(self):
        return self._db

    def install(self):
        self._ruby_environment.first_time_setup()

        self._db.install_server()
        self._db.install_client()

        self._host_machine.create_project_folder()

        if not self._project_already_cloned():
            self._vcs.clone_project()

        self._rails_project.first_time_setup()

        self._ruby_webserver.configure_server()
        self._ruby_webserver.restart_server()

    def upgrade(self):
        self._vcs.pull()

        self._rails_project.after_pull_update()

        self._ruby_webserver.restart_server()

    def rollback_db_to_latest_backup(self):
        raise NotImplementedError("Not implemented yet! Please do it :)")

    def _project_already_cloned(self):
        return self._host_machine.path_exists(os.path.join(self._host_machine.project_path(), 'app'))
