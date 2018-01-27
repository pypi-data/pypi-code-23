"""
make2help

See: https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
"""

import re


def parse_makefile(lines):
    """
    parse makefine lines.
    """
    lines = [line for line in lines if line != '']
    help_pattern = re.compile('(?<=^## ).+')
    target_pattern = re.compile('.+(?=:)')
    for num, line in enumerate(lines):
        find_target = target_pattern.search(line)
        if find_target:
            target = find_target.group()
            help_ = help_pattern.search(lines[num - 1])
            if num != 0 and help_:
                detail = help_.group()
            else:
                detail = ''
            yield target, detail


def prepare_makefile_lines(makefile_path):
    """return makefile content"""
    with open(makefile_path, 'r') as makefile:
        lines = makefile.readlines()
    return lines


def format_makehelp(target, detail):
    """
    return "{target}:\t{detail}"
    """
    return '{}:\t{}'.format(target, detail)
