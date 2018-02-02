from os.path import join, isfile, isdir, exists
from os import getcwd
from kooki.config import get_kooki_dir_recipes, get_kooki_dir_jars


def search_jar(jar):
    ret_jar_path = None
    user_jars_dir = get_kooki_dir_jars()
    jar_path = join(user_jars_dir, jar)
    if isdir(jar_path):
        ret_jar_path = jar_path
    return ret_jar_path


def search_recipe(recipe):
    ret_recipe_path = None
    user_recipes_dir = get_kooki_dir_recipes()
    recipe_path = join(user_recipes_dir, recipe)
    if isdir(recipe_path):
        ret_recipe_path = recipe_path
    return ret_recipe_path


def get_search_paths(jars, recipe):
    directories = []
    directories.append(get_local_path())
    directories += get_jars_path(jars, recipe)
    return directories


def get_local_path():
    return getcwd()


def get_jars_path(jars, recipe):
    user_jars_dir = get_kooki_dir_jars()
    directories = []
    for jar in jars:
        jar_path = join(user_jars_dir, jar)
        directories.append(jar_path)
        recipe_jar_path = join(jar_path, recipe)
        directories.append(recipe_jar_path)
    return directories


def search_file(jars, recipe, filename):
    ret_file_path = None
    ret_file_path = search_file_in_local(filename)
    if not ret_file_path:
        ret_file_path = search_file_in_jars(jars, recipe, filename)
    return ret_file_path


def search_file_or_dir(jars, recipe, filename):
    ret_file_path = None
    ret_file_path = search_file_in_local(filename, test=exists)
    if not ret_file_path:
        ret_file_path = search_file_in_jars(jars, recipe, filename, test=exists)
    return ret_file_path


def search_file_in_local(filename, test=isfile):
    ret_file_path = None
    file_path = join(getcwd(), filename)
    if test(file_path):
        ret_file_path = file_path
    return ret_file_path


def search_file_in_jars(jars, recipe, filename, test=isfile):
    user_jars_dir = get_kooki_dir_jars()
    ret_file_path = None
    for jar in jars:
        jar_path = join(user_jars_dir, jar)
        ret_file_path = search_file_in_jar(jar_path, recipe, filename, test)
        if ret_file_path:
            break
    return ret_file_path


def search_file_in_jar(jar_path, recipe, filename, test=isfile):
    ret_file_path = search_file_in_jar_recipe(jar_path, recipe, filename, test)
    if not ret_file_path:
        ret_file_path = search_file_in_jar_local(jar_path, filename, test)
    return ret_file_path


def search_file_in_jar_recipe(jar_path, recipe, filename, test=isfile):
    ret_file_path = None
    recipe_jar_path = join(jar_path, recipe)
    file_path = join(recipe_jar_path, filename)
    if test(file_path):
        ret_file_path = file_path
    return ret_file_path


def search_file_in_jar_local(jar_path, filename, test=isfile):
    ret_file_path = None
    file_path = join(jar_path, filename)
    if test(file_path):
        ret_file_path = file_path
    return ret_file_path
