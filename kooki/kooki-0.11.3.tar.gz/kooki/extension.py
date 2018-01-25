import os, em, types
from kooki.tools import get_front_matter
from kooki.common import apply_template

def load_extensions(jars, recipe):
    current = os.getcwd()
    extensions = {}
    path = os.path.join(current, 'extensions')
    if os.path.isdir(path):
        load_extensions_in_directory(path, extensions)
    for jar in jars:
        path = os.path.join(jar, recipe, 'extensions')
        if os.path.isdir(path):
            load_extensions_in_directory(path, extensions)
        path = os.path.join(jar, 'extensions')
        if os.path.isdir(path):
            load_extensions_in_directory(path, extensions)
    return extensions


def load_extensions_in_directory(directory, extensions):
    for file_name in os.listdir(directory):
        path = os.path.join(directory, file_name)
        extension_name = os.path.splitext(file_name)[0]
        if not extension_name in extensions:
            extensions[extension_name] = path


def caller(file_full_path, metadata={}):
    def call(*args, **kwargs):
        with open(file_full_path,'r') as f:
            file_content = f.read()
            metadata.update(**kwargs)
            result = apply_template(file_content, metadata)
            return result
    return call
