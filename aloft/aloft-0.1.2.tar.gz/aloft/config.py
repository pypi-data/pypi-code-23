from aloft import input


def get_profile():
    return get_aloft_config()['profile']


def get_roles():
    return get_aloft_config()['roles']


def get_aloft_config():
    return input.read_yaml_file(get_aloft_config_filename())


def get_aloft_config_filename():
    aloft_config_directory = get_aloft_config_directory()
    return f'{aloft_config_directory}/config.yaml'


def get_aloft_config_directory():
    return input.get_directory_from_environment('ALOFT_CONFIG', '~/.aloft')
