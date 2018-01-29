import os

GIT_FOLDER = '.git'
GIT_HEAD = 'HEAD'


def is_git(path):
    return os.path.isdir(os.path.join(path, GIT_FOLDER))


def find_root(path):
    if is_git(path):
        return path
    else:
        next_path = os.path.dirname(path)
        if next_path != path:
            return find_root(next_path)
        else:
            return None


def get_revision(path):
    return follow_sym_links(os.path.join(path, GIT_FOLDER), GIT_HEAD)


def follow_sym_links(root, link):
    with open(os.path.join(root, link), 'r') as f:
        content = f.read()

    if content.startswith("ref:"):
        next_link = content.split(' ')[1].strip()
        return follow_sym_links(root, next_link)
    else:
        return content.strip()
