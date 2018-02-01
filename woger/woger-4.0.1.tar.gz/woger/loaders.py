import os


def default_loader(target_path:str, workspace_root:str, action:str):
    from .workspace import Workspace

    ws = Workspace.construct(workspace_root)
    with ws.track(action):
        name = os.path.split(target_path)[-1]  # type: str
        stripped_name = name.lstrip('.')
        is_dir = '.' not in stripped_name

        if is_dir:
            os.makedirs(str(target_path))

    return True
