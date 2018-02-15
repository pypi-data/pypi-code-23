""" unittest.
"""
import os

def unittest(loader, project=None, variant=None, *args):
    loader.setup_virtualenv()

    project, variant = loader.setup_project_env(project, variant)

    config = loader.config.get('configuration', {})
    config = config.get(variant, {})
    config = config.get(project, {})

    loader.setup_shell_env(config.get('shell_env', {}))

    python_bin = loader.get_python_bin()

    binargs = [python_bin, '-m', 'unittest'] + list(args)
    os.execvp(binargs[0], binargs)


commands = (unittest,)
