import re


def version(path, short=False):
    for line in open(path):
        if line.startswith('__version__'):
            result = line.strip().split()[-1][1:-1]
            break
    if short:
        result = re.match(r'([0-9]+\.)+[0-9]+', result)
    return result
