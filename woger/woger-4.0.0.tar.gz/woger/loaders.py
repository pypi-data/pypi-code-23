import os


def default_loader(target_path, workspace_root, action_name):
    from .workspace import Workspace

    ws = Workspace.construct(workspace_root)
    with ws.track(action_name):
        is_dir = '.' not in target_path.name

        if is_dir:
            os.makedirs(str(target_path))

    return True
