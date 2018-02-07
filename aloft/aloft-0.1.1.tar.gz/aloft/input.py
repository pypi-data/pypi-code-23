import jinja2
import os
import yaml


def get_directory_from_environment(environment_key, default_directory_name=None):
    directory_name = os.path.expanduser(os.environ.get(environment_key, default_directory_name))
    validate_config_directory(directory_name, environment_key)
    return directory_name


def validate_config_directory(config_directory, environment_key):
    if config_directory is None:
        raise NotADirectoryError(f'{environment_key} environment variable has not been set')
    elif not os.path.isdir(config_directory):
        raise NotADirectoryError(f'{environment_key} must reference a directory: {config_directory}')


def render_template_file(template_filename, context):
    path, filename = os.path.split(template_filename)
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path)
    ).get_template(filename).render(context)


def read_yaml_file(filename):
    with open(filename, 'r') as stream:
        return yaml.load(stream)

