# -*- coding: utf-8 -*-

import subprocess

def output_stack():
    import traceback
    import sys
    traceback.print_exc(file=sys.stdout)

def shell(command):
    """Execute a shell command and returns the value"""
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    if err:
        raise OSError('shell returns {0}'.format(err))
    return output


def import_dir(module, module_dir=None, project_dir=None):
    """get module info without loading"""
    if module_dir:
        try:
            s = shell('python -c "import os;os.chdir(\'{path}\');import {module} as key;print(dir(key))"'.format(
                path=module_dir, module=module))
            if s:
                return eval(s)
        except:
            pass
    if project_dir:
        try:
            s = shell('python -c "import os;os.chdir(\'{path}\');import {module} as key;print(dir(key))"'.format(
                path=project_dir, module=module))
            if s:
                return eval(s)
        except:
            pass
    try:
        s = shell('python -c "import {module} as key;print(dir(key))"'.format(module=module))
        return eval(s)
    except:
        pass
    return None
