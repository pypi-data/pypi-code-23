import re

first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def snake_case(camel_case):
    snake = first_cap_re.sub(r'\1_\2', camel_case)
    return all_cap_re.sub(r'\1_\2', snake).lower()




