import os


def create_dir(path):
    os.makedirs(path, exist_ok=True)


def create_file(path):
    if not os.path.exists(path):
        create_dir(os.path.split(path)[0])
        with open(path, 'w'):
            pass

def is_dir(path):
    name = os.path.split(path)[-1]  # type: str
    stripped_name = name.lstrip('.')
    return '.' not in stripped_name


def default_loader(path:str, root:str, action:str):
    from .base_path_structure import BasePathStructure

    ws = BasePathStructure(root)
    with ws.track(action):
        if is_dir(path):
            create_dir(path)
        else:
            create_file(path)
