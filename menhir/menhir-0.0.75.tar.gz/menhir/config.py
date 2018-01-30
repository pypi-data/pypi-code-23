# menhir configuration
import logging
import os

log = logging.getLogger(__name__)


def project_config(path="menhir-config.yaml", dir=os.getcwd()):
    """Return the project configuration in dir_path."""
    from os.path import abspath, basename, dirname, isabs, join
    from menhir.fileutils import load_yaml
    if not isabs(path) and path != "-":
        path = join(dir, path)
    config = load_yaml(path) or {}
    if 'project-name' not in config:
        config['project-name'] = basename(dirname(abspath(path)))
    return config
