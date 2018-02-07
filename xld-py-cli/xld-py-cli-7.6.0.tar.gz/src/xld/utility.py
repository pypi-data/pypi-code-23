import re
from os import path


def find_uploads(content):
    findall = re.findall('upload\([\'|"](.*)[\'|"]\)', content.decode("utf-8"))
    # print("Atifacts for upload:", findall)
    return findall


def read_files(names, file_path):
    return [__resolve_file(name, file_path) for name in names]


def __resolve_file(name, folder):
    file = path.abspath(path.join(folder, name))
    if not path.exists(file):
        raise Exception('{0} does not exists in {1}'.format(name, folder))
    return file
