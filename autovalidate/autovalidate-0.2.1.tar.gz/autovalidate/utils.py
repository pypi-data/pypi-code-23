def indent(string, level=1):
    return '\n'.join(('\t' * level) + line
                     for line in string.splitlines())
