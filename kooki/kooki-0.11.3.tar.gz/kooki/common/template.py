import em, re
from kooki.tools import get_front_matter
from collections import OrderedDict
from kooki.exception import KookiException

def apply_template(data, metadata):

    result = None

    if isinstance(data, list):
        result = []
        for content in data:
            result.append(apply_interpreter(content, metadata))

    elif isinstance(data, OrderedDict):
        result = OrderedDict()
        for file_path, file_content in data.items():
            front_matter, content = get_front_matter(file_content)
            metadata.update(front_matter)
            result[file_path] = apply_interpreter(content, metadata)

    elif isinstance(data, dict):
        result = {}
        for file_path, file_content in data.items():
            front_matter, content = get_front_matter(file_content)
            metadata.update(front_matter)
            result[file_path] = apply_interpreter(content, metadata)

    elif isinstance(data, str):
        result = ''
        result = apply_interpreter(data, metadata)

    else:
        raise Exception('templating bad data type {}'.format(type(data)))

    return result


def apply_interpreter(content, metadata):
    interpreter = em.Interpreter()
    interpreter.setPrefix('@')

    result = interpreter.expand(content, metadata)

    return result
