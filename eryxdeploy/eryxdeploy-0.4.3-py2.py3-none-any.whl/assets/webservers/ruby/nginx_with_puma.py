import os

from eryx_deploy.assets.webservers.abs_webserver import Webserver
from eryx_deploy.utils.interactive_console import InteractiveConsole


class NginxWithPumaWebserver(Webserver):
    """
    Slightly coupled to Ruby on Rails... Will need some changes to support other FW.
    """

    def __init__(self, machine, webapp_name, ruby_environment):
        super(NginxWithPumaWebserver, self).__init__(machine=machine, webapp_name=webapp_name)
        self._ruby_environment = ruby_environment

    def restart_server(self):
        self._machine.run('sudo systemctl restart puma-%s.service' % self._webapp_name)
        self._machine.run('sudo service nginx restart')

    def configure_server(self):
        self._machine.install_nginx()
        # No need to install Puma es it's the default for Rails apps.

        self._configure_nginx()
        self._configure_puma()
        self._configure_systemd_for_puma()

    # configure nginx

    def _configure_nginx(self):
        if self._nginx_already_configured():
            InteractiveConsole.show_info("Nginx already configured for this project, skipping...")
            return

        config_file = '/etc/nginx/sites-available/%s' % self._webapp_name
        self._machine.run('sudo touch %s' % config_file)
        self._machine.append(config_file, self._nginx_project_configuration(), use_sudo=True)

        self._machine.run('sudo ln -s %s /etc/nginx/sites-enabled' % config_file)

    def _nginx_already_configured(self):
        config_file = '/etc/nginx/sites-available/%s' % self._webapp_name
        return self._machine.path_exists(config_file)

    def _nginx_project_configuration(self):
        configuration = 'upstream %s_server {\n' % self._webapp_name + \
                        '\tserver unix:%s;\n' % self._socket_path() + \
                        '}\n\n'

        configuration += 'server {\n' + \
                         '\tlisten 80;\n' + \
                         '\tserver_name %s;\n\n' % self._machine.hostname() + \
                         '\tlocation /favicon.ico { access_log off; log_not_found off; }\n' + \
                         '\troot %s;\n' % os.path.join(self._webapp_project_path(), 'public')

        configuration += '\tlocation / {\n' + \
                         '\t\tproxy_redirect off;\n' + \
                         '\t\tproxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n' + \
                         '\t\tproxy_set_header Host $http_host;\n\n' + \
                         '\t\tproxy_read_timeout 1200s;\n' + \
                         '\t\tproxy_connect_timeout 1200s;\n\n' + \
                         '\t\tproxy_pass http://%s_server;\n' % self._webapp_name + \
                         '\t}\n'

        if self._using_precompiled_assets():
            # When using precompiled assets, we want Nginx to serve them from 'public/assets' directly
            configuration += '\tlocation ~* ^/assets/ {\n' + \
                             '\t\texpires 1y;\n' + \
                             '\t\tadd_header Cache-Control public;\n' + \
                             '\t}\n'

        configuration += '}'

        return configuration

    # configure puma

    def _configure_puma(self):
        if self._puma_already_configured():
            InteractiveConsole.show_info("Puma already configured for this project, skipping...")
            return

        with self._machine.cd(self._webapp_project_path()):
            self._machine.run('mkdir -p tmp/pids')
            self._machine.run('mkdir -p tmp/sockets')
            self._machine.run('touch %s' % self._puma_config_file())
            self._machine.append(self._puma_config_file(), self._puma_project_configuration())

    def _puma_already_configured(self):
        config_file = os.path.join(self._webapp_project_path(), self._puma_config_file())
        return self._machine.path_exists(config_file)

    def _puma_project_configuration(self):
        log_path = "%s/log" % self._webapp_project_path()
        pids_path = "%s/tmp/pids" % self._webapp_project_path()

        configuration = 'workers 2\n'
        configuration += 'threads 1, 6\n'

        configuration += 'rails_env = "%s"\n' % self._ruby_environment.get_env_var('RAILS_ENV')
        configuration += 'environment rails_env\n'

        configuration += 'bind \"unix://%s\"\n' % self._socket_path()

        configuration += 'loglevel = "info"\n'
        configuration += 'stdout_redirect "%s/%s.stdout.log", "%s/%s.stderr.log", true\n' % \
                         (log_path, self._webapp_name, log_path, self._webapp_name)

        configuration += 'pidfile "%s/%s.pid"\n' % (pids_path, self._webapp_name)
        configuration += 'state_path "%s/%s.state"\n' % (pids_path, self._webapp_name)
        configuration += 'activate_control_app\n'

        configuration += 'on_worker_boot do\n'
        configuration += '\trequire "active_record"\n'
        configuration += '\tActiveRecord::Base.connection.disconnect! rescue ActiveRecord::ConnectionNotEstablished\n'
        configuration += '\tActiveRecord::Base.establish_connection(YAML.load_file("%s/config/database.yml")[rails_env])\n' \
                         % self._webapp_project_path()
        configuration += 'end'

        return configuration

    def _configure_systemd_for_puma(self):
        if self._systemd_puma_already_configured():
            InteractiveConsole.show_info("Systemd already configured for Puma, skipping...")
            return

        config_file = '/etc/systemd/system/puma-%s.service' % self._webapp_name
        self._machine.run('sudo touch %s' % config_file)
        self._machine.append(config_file, self._systemd_puma_configuration(), use_sudo=True)

        self._machine.run('sudo systemctl daemon-reload')
        self._machine.run('sudo systemctl enable puma-%s.service' % self._webapp_name)
        self._machine.run('sudo systemctl start puma-%s.service' % self._webapp_name)

    def _systemd_puma_already_configured(self):
        config_file = '/etc/systemd/system/puma-%s.service' % self._webapp_name
        return self._machine.path_exists(config_file)

    def _systemd_puma_configuration(self):
        configuration = '[Unit]\n'
        configuration += 'Description=Puma HTTP Server for %s\n' % self._webapp_name
        configuration += 'After=network.target\n\n'

        configuration += '[Service]\n'
        configuration += 'Type=simple\n'
        configuration += 'User=%s\n' % self._machine.current_user()
        configuration += 'Environment="%s=%s"\n' % (self._ruby_environment.ruby_version_env_var_key(),
                                                    self._ruby_environment.ruby_version())
        configuration += 'WorkingDirectory=%s\n' % self._webapp_project_path()
        configuration += 'ExecStart=%s exec puma -C %s\n' % (self._bundle_command_path(), self._puma_config_file())
        configuration += 'Restart=always\n\n'

        configuration += '[Install]\n'
        configuration += 'WantedBy=multi-user.target'

        return configuration

    # private

    def _bundle_command_path(self):
        return self._ruby_environment.command_path('bundle')

    def _webapp_project_path(self):
        return self._machine.project_path()

    def _socket_path(self):
        return "%s/tmp/sockets/%s.sock" % (self._webapp_project_path(), self._webapp_name)

    def _puma_config_file(self):
        return "config/puma.%s.rb" % self._ruby_environment.get_env_var('RAILS_ENV')

    def _using_precompiled_assets(self):
        # TODO: This check can probably be done with more precision. Custom environments may break.
        return self._ruby_environment.get_env_var('RAILS_ENV') == 'production'
