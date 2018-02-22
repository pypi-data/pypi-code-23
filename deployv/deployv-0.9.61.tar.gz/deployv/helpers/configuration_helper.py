import os
import errno
import logging
import simplejson as json
from jinja2 import Template
from deployv.helpers import json_helper, utils
from deployv.base.errors import ParameterError
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

_logger = logging.getLogger(__name__)


class DeployvConfig(object):

    def __init__(self, worker_config=None, deploy_config=None):
        self._extras = {}
        self.postgres = {}
        self.deployer = {}
        self.http = {}
        self.rmq = {}
        self.instance_config = {}
        self.container_config = {}
        self.worker_config = self.parse_config(worker_config)
        self._deploy_config = deploy_config or {}
        self.generate_configuration(self._deploy_config)

    def __getattr__(self, name):
        return self._extras.get(name, False)

    def check_config(self, command):
        required_params = {
            'create': ['_deploy_config'],
            'deactivate': ['_deploy_config'],
            'restore': ['_deploy_config'],
            'backup': ['_deploy_config'],
            'deactivate_backup': ['_deploy_config', 'temp_folder', 'backup_src', 'prefix'],
            'updatedb': ['_deploy_config'],
            'update_production': ['backup_src', 'expected_backup_size', 'temp_folder'],
            'build_image': ['_deploy_config'],
        }
        missing_params = []
        if command not in required_params.keys():
            return
        for param in required_params.get(command):
            value = (getattr(self, param) if hasattr(self, param) else
                     self._extras.get(param, False))
            if not value:
                missing_params.append(param)
        if missing_params:
            raise ParameterError(
                'Missing required parameters for the {cmd} command: {params}'
                .format(cmd=command, params=','.join(missing_params)))

    def _get_backup_src(self, backup_src):
        backup_src = backup_src or utils.get_backup_src(
            self._deploy_config, self.worker_config)
        return os.path.expanduser(backup_src) if backup_src else False

    def _get_temp_folder(self, temp_folder):
        temp_folder = (temp_folder or
                       self.worker_config.has_option('deployer', 'temp_folder') and
                       self.worker_config.get('deployer', 'temp_folder') or '/tmp')
        res = utils.makedir(temp_folder)
        return res

    def _get_prefix(self, prefix):
        prefix = prefix or self._deploy_config.get('instance', {}).get('prefix')
        return prefix

    def parse_config(self, additional_config_file=None):
        """Loads and returns the parsed config files in a ConfigParser object.

        The config files are loaded in this order:

        1. /etc/deployv/deployv.conf
        2. /etc/deployv/conf.d/*.conf
        3. ~/.config/deployv/deployv.conf
        4. ~/.config/deployv/conf.d/*.conf
        5. All files received in additional_config_files.

        :param additional_config_file: Additional .conf file to load.
        :type additional_config_files: String

        :returns: The parsed config files.
        :rtype: ConfigParser
        """
        config = self.worker_config or ConfigParser()
        default_config_file = 'deployv/config/deployv.conf'
        config_files = [default_config_file]
        main_dirs = ['/etc/deployv', os.path.expanduser('~/.config/deployv')]
        for main_dir in main_dirs:
            main_config_file = os.path.join(main_dir, 'deployv.conf')
            if os.access(main_config_file, os.F_OK):
                config_files.append(main_config_file)
            addons_dir = os.path.join(main_dir, 'conf.d')
            if os.path.isdir(addons_dir):
                for filename in os.listdir(addons_dir):
                    filepath = os.path.join(addons_dir, filename)
                    if os.path.isfile(filepath) and filename.endswith('.conf'):
                        config_files.append(filepath)
        if len(config_files) == 1:
            _logger.warn("Warning: no config file detected in the config "
                         "paths. You can create a `deployv.conf` file in "
                         "`/etc/deployv/` or `~/.config/deployv/` paths. "
                         "You can also run `deployvcmd setup_config` to "
                         "automatically create the config files for you.")
        if additional_config_file:
            config_files.append(additional_config_file)
        if config_files:
            _logger.info("Loading config files: %s", ", ".join(config_files))
            loaded_files = config.read(config_files)
            if len(config_files) != len(loaded_files):
                _logger.warn("Error loading config files: %s",
                             ", ".join(set(config_files) - set(loaded_files)))
        self.set_worker_config_sections(config)
        return config

    def set_worker_config_sections(self, config):
        """ Sets each section of the worker configuration as an attribute of the config object,
        each attribute will contain a dictionary with the keys of that section. This is so we
        can access to all the configuration in an easier way.

        :param config: Worker configuration
        :type config: ConfigParser object
        """
        booleans = ['use_template', 'use_nginx', 'rmq_ssl']
        integers = ['db_port', 'workers', 'max_instances', 'jobs', 'rmq_port', 'rmq_timeout']
        if not isinstance(config, ConfigParser):
            raise ParameterError('worker_config: Invalid type {}'.format(type(config)))
        for section in config.sections():
            values = dict(config.items(section))
            for key in values.keys():
                if key in booleans:
                    values.update({key: config.getboolean(section, key)})
                elif key in integers:
                    values.update({key: config.getint(section, key)})
            setattr(self, section, values)

    def generate_configuration(self, config):
        """ Configures the current instance of this class with the provided config dict.
        This method sets the `instance_config` and the  `container_config` attributes
        based on the `instance` and `container_config` keys in the config dict, it
        also adds an attribute for each key in the `group_config` key. Each one of these params
        can have a `_get_{attribute name}` method with special logic to help this method decide
        what value will be stored in that new attribute.

        :param config: Configuration that will be used to prepare this object to be used by deployv
        :type config: dict
        """
        parsed_config = json_helper.load_json(config)
        if not isinstance(parsed_config, dict):
            raise ParameterError('deploy_config: Invalid type: {tp}'.format(tp=type(config)))
        if parsed_config.get('instance', {}).get('instance_type') != 'production':
            parsed_config = utils.merge_config(parsed_config)
        res = json.loads(Template(json.dumps(parsed_config)).render(parsed_config))
        # Parameters that require extra logic before setting them
        special_params = ['backup_src', 'temp_folder', 'prefix']
        self._deploy_config = res
        self.instance_config = res.get('instance') or {}
        self.container_config = res.get('container_config') or {}
        if not res.get('group_config'):
            res.update({'group_config': {}})
        for param in special_params:
            get_method = '_get_' + param
            if not hasattr(self, get_method):
                continue
            func = getattr(self, get_method)
            new_val = func(res.get('group_config').get(param, False))
            res.get('group_config').update({param: new_val})
        self._extras = res.get('group_config')

    def setup_config_dirs(self):
        _logger.info("Writing config files")
        default_config_file = 'deployv/config/deployv.conf'
        for main_dir in ['/etc/deployv', os.path.expanduser('~/.config/deployv')]:
            config_file_name = os.path.join(main_dir, 'deployv.conf')
            error_msg = "Couldn't write config file: '%s' (skipped)"
            ok_msg = "Created config file: '%s'"
            addon_dir = os.path.join(main_dir, 'conf.d')
            is_user_dir = os.path.expanduser('~/') in main_dir
            try:
                os.makedirs(addon_dir)
            except OSError as error:
                if error.errno != errno.EEXIST:
                    _logger.warn(error_msg, config_file_name)
                    continue
            else:
                if is_user_dir:
                    for path in [main_dir.replace('/deployv', ''), main_dir, addon_dir]:
                        self._fix_ownership(path)
            config = ConfigParser()
            config.read([default_config_file, config_file_name])
            try:
                with open(config_file_name, 'w+') as config_file:
                    config.write(config_file)
            except (OSError, IOError) as error:
                _logger.warn(error_msg, config_file_name)
            else:
                _logger.info(ok_msg, config_file_name)
                if is_user_dir:
                    self._fix_ownership(config_file_name)
        self.worker_config = self.parse_config()

    def _fix_ownership(self, path):
        uid = os.environ.get('SUDO_UID')
        gid = os.environ.get('SUDO_GID')
        if uid is not None:
            os.chown(path, int(uid), int(gid))


def get_config(config_file=None):
    config = DeployvConfig(worker_config=config_file)
    return config.worker_config
