import jinja2
import os


def get_directory_from_environment(environment_key):
    base_cluster_config_directory = os.environ[environment_key]
    validate_config_directory(base_cluster_config_directory, environment_key)
    return base_cluster_config_directory


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
