import pretty_output, os, traceback

from collections import OrderedDict

from kooki.jars import search_file, search_file_or_dir, search_recipe, search_jar
from kooki.extension import load_extensions, caller
from kooki.exception import MissingRecipe, MissingTemplate, MissingMetadata, MissingContent, InvalidRecipe
from kooki.common import Metadata, parse_metadata

output = []

def output_search_start():
    global output
    output = []


def output_search(path, fullpath):
    if fullpath:
        output.append({'name': path, 'status': '[found]', 'path': fullpath})
    else:
        output.append({'name': path, 'status': ('[missing]', 'red'), 'path': ''})


def output_search_finish():
    pretty_output.infos(output, [('name', 'blue'), ('status', 'green'), ('path', 'cyan')])


def process_document(document_origin):
    document = document_origin.copy()
    recipe = document.recipe
    jars = document.jars

    # jars
    full_path_jars = []
    for jar in document.jars:
        jar_full_path = search_jar(jar)
        full_path_jars.append(jar_full_path)
    document.jars = full_path_jars

    # template
    pretty_output.title_3('template')
    output_search_start()
    file_full_path = search_file(jars, recipe, document.template)
    output_search(document.template, file_full_path)
    if file_full_path:
        with open(file_full_path,'r') as f:
            file_read = f.read()
        document.template = file_read
        output_search_finish()
    else:
        output_search_finish()
        raise MissingTemplate(jars, recipe, document.template)

    # metadata
    pretty_output.title_3('metadata')
    metadata_full_path = {}
    output_search_start()
    for metadata in document.metadata:
        file_full_path = search_file(jars, recipe, metadata)
        output_search(metadata, file_full_path)
        if file_full_path:
            with open(file_full_path,'r') as f:
                file_read = f.read()
            metadata_full_path[file_full_path] = file_read
        else:
            output_search_finish()
            raise MissingMetadata(jars, recipe, metadata)
    document.metadata = metadata_full_path
    output_search_finish()

    document.metadata = parse_metadata(document.metadata)

    # thing for more

    def read(document, metadata={}):
        def callback(file_path):
            file_full_path = search_file(document.jars, document.recipe, file_path)
            ret_content = ''
            if file_full_path:
                with open(file_full_path,'r') as stream:
                    ret_content = stream.read()
            return ret_content
        return callback

    def path(document):
        def callback(file_path):
            file_full_path = search_file_or_dir(document.jars, document.recipe, file_path)
            return file_full_path
        return callback


    others = {
        'read': read(document),
        'path': path(document)}

    document.metadata.update(others)

    # extensions
    pretty_output.title_3('extensions')
    output_search_start()
    extensions_raw = load_extensions(document.jars, document.recipe)
    extensions = Metadata()
    for extension_name, extension_path in extensions_raw.items():

        splitted = extension_name.split('.')
        current = extensions
        for s in splitted[:-1]:
            if not s in current:
                current[s] = Metadata()
            current = current[s]
        current[splitted[-1]] = caller(extension_path, document.metadata)

        output_search(extension_name, extension_path)
    output_search_finish()

    # content
    pretty_output.title_3('content')
    content_full_path = OrderedDict()
    output_search_start()
    for content in document.content:
        file_full_path = search_file(jars, recipe, content)
        output_search(content, file_full_path)
        if file_full_path:
            with open(file_full_path,'r') as f:
                file_read = f.read()
            content_full_path[file_full_path] = file_read
        else:
            output_search_finish()
            raise MissingContent(jars, recipe, content)
    document.content = content_full_path
    output_search_finish()

    # recipe
    pretty_output.title_3('recipe')
    recipe_full_path = search_recipe(recipe)

    if not recipe_full_path or not os.path.isdir(recipe_full_path):
        raise MissingRecipe(recipe)

    try:
        import imp
        fp, pathname, description = imp.find_module('recipe', [recipe_full_path])
        recipe_module = imp.load_module('recipe', fp, pathname, description)
        recipe_module.recipe(document, extensions)

    except Exception as e:
        raise InvalidRecipe(recipe, traceback.format_exc())
