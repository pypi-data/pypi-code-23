import re


def multiple_replace(dic: dict, text: str, pattern: bytes):
    return re.sub(pattern, lambda m: dic[m.group().strip()], str(text))


def generate_multiple_replace_pattern(dictionary):
    pattern = "|".join(map(re.escape, dictionary.keys()))
    pattern = "(%s)" % pattern
    return pattern
