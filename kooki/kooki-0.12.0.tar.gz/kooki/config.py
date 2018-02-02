import os, yaml

from kooki.exception import YamlErrorConfigFileBadType, YamlErrorConfigFileParsing
from kooki.exception import NoConfigFileFound

resource_dir_env = 'KOOKI_DIR'
resource_dir_default = '~/.kooki'

jar_manager_env = 'KOOKI_JAR_MANAGER'
jar_manager_default = ['https://gitlab.com/kooki/jar_manager/raw/master/jars.yml']

recipe_manager_env = 'KOOKI_RECIPE_MANAGER'
recipe_manager_default = ['https://gitlab.com/kooki/recipe_manager/raw/master/recipes.yml']


def get_kooki_dir():
    resource_dir = os.environ.get(resource_dir_env)
    if not resource_dir:
        resource_dir = os.path.expanduser(resource_dir_default)
    return resource_dir


def get_kooki_dir_jars():
    resources_dir = get_kooki_dir()
    jars_dir = os.path.join(resources_dir, 'jars')
    return jars_dir


def get_kooki_dir_recipes():
    resources_dir = get_kooki_dir()
    recipes_dir = os.path.join(resources_dir, 'recipes')
    return recipes_dir


def get_kooki_jar_manager():
    jar_manager = os.environ.get(jar_manager_env)
    if jar_manager:
        jar_manager = yaml.safe_load(jar_manager)
    else:
        jar_manager = jar_manager_default
    return jar_manager


def get_kooki_recipe_manager():
    recipe_manager = os.environ.get(recipe_manager_env)
    if recipe_manager:
        recipe_manager = yaml.safe_load(recipe_manager)
    else:
        recipe_manager = recipe_manager_default
    return recipe_manager


def read_config_file(config_file_name):
    if os.path.isfile(config_file_name):
        with open(config_file_name, 'r') as stream:
            try:
                content = stream.read()
                config = yaml.safe_load(content)
                if not isinstance(config, dict):
                    raise YamlErrorConfigFileBadType(type(config))
                return config
            except yaml.YAMLError as exc:
                raise YamlErrorConfigFileParsing(exc)
    else:
        raise NoConfigFileFound(config_file_name)
