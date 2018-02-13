import empy, copy
from kooki.tools import get_front_matter
from collections import OrderedDict
from kooki.common import Metadata

def apply_template(data, metadata):

    result = None

    if isinstance(data, list):
        result = []
        for file_content in data:
            front_matter, content = get_front_matter(file_content)
            unique_metadata = get_metadata(front_matter, metadata)
            result.append(apply_interpreter(content, unique_metadata))

    elif isinstance(data, OrderedDict):
        result = OrderedDict()
        for file_path, file_content in data.items():
            front_matter, content = get_front_matter(file_content)
            unique_metadata = get_metadata(front_matter, metadata)
            result[file_path] = apply_interpreter(content, unique_metadata)

    elif isinstance(data, dict):
        result = {}
        for file_path, file_content in data.items():
            front_matter, content = get_front_matter(file_content)
            unique_metadata = get_metadata(front_matter, metadata)
            result[file_path] = apply_interpreter(content, unique_metadata)

    elif isinstance(data, str):
        result = ''
        front_matter, content = get_front_matter(data)
        unique_metadata = get_metadata(front_matter, metadata)
        result = apply_interpreter(content, unique_metadata)

    else:
        raise Exception('templating bad data type {}'.format(type(data)))

    return result


def get_metadata(front_matter, metadata):
    metadata_copy = Metadata()
    metadata_copy.update(front_matter)
    metadata_copy.update(metadata)
    return metadata_copy

def apply_interpreter(content, metadata):
    interpreter = empy.Interpreter()
    interpreter.setPrefix('@')
    result = interpreter.expand(content, metadata)
    return result
