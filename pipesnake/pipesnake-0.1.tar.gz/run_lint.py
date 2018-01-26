# -*- coding: utf-8 -*-

import logging
import os

from pylint import lint


def get_py_files(base_path):
    f = []
    for root, dirs, files in os.walk(base_path):
        for name in files:
            if name.endswith('.py'):
                f.append(os.path.normpath(os.path.join(root, name)))
    return f


def main():
    params = ['-j', '4', '--msg-template={path}:{line}: [{msg_id}({symbol}), {obj}] {msg}']
    files = get_py_files('pipesnake')
    params.extend(files)
    logging.info('pylint params: %s', ' '.join(params))
    logging.info('Going to lint: %s files', len(files))
    lint.Run(params)


if __name__ == '__main__':
    main()
