import empy, copy
from kooki.tools import get_front_matter
from collections import OrderedDict


def apply_template(data, metadata):

    result = None
    metadata_copy = metadata.copy()

    if isinstance(data, list):
        result = []
        for content in data:
            result.append(apply_interpreter(content, metadata_copy))

    elif isinstance(data, OrderedDict):
        result = OrderedDict()
        for file_path, file_content in data.items():
            front_matter, content = get_front_matter(file_content)
            metadata_copy.update(front_matter)
            result[file_path] = apply_interpreter(content, metadata_copy)

    elif isinstance(data, dict):
        result = {}
        for file_path, file_content in data.items():
            front_matter, content = get_front_matter(file_content)
            metadata_copy.update(front_matter)
            result[file_path] = apply_interpreter(content, metadata_copy)

    elif isinstance(data, str):
        result = ''
        result = apply_interpreter(data, metadata_copy)

    else:
        raise Exception('templating bad data type {}'.format(type(data)))

    return result


def apply_interpreter(content, metadata):
    interpreter = empy.Interpreter()
    interpreter.setPrefix('@')
    result = interpreter.expand(content, metadata)
    return result
