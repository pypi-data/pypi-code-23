import os
from kooki.common import apply_template, Metadata
from kooki.tools import get_front_matter


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
        if extension_name not in extensions:
            extensions[extension_name] = path


def caller(file_full_path, metadata={}):
    def call(*args, **kwargs):
        with open(file_full_path, 'r') as f:
            file_content = f.read()
            front_matter, content = get_front_matter(file_content)
            metadata_copy = Metadata()
            metadata_copy.update(front_matter)
            metadata_copy.update(metadata)
            metadata_copy.update(**kwargs)
            result = apply_template(content, metadata_copy)
            return result
    return call
