from collections import Iterable
from io import StringIO
import sys

try:
    from regex import compile, DEBUG
except ImportError:
    from re import compile, DEBUG


def unescape(pattern: str):
    """Remove any escape that does not change the regex meaning"""
    sys.stdout = StringIO()
    parsed_pattern = compile(pattern)
    original_debug = sys.stdout.getvalue()
    index = len(pattern)
    while index >= 0:
        index -= 1
        character = pattern[index]
        if character != '\\':
            continue
        removed_escape = pattern[:index] + pattern[index+1:]
        try:
            escape_removed_parse = parse(removed_escape)
        except sre_error:
            continue
        if equal_subpatterns(escape_removed_parse, parsed_pattern):
            pattern = removed_escape
            parsed_pattern = parse(removed_escape)
    return pattern


def equal_subpatterns(sp1, sp2):
    """Compare SubPattern instances for equality."""
    # The sre_parse.SubPattern class does not have __eq__ method
    # and its items may contain nested SubPatterns.
    for p1, p2 in zip(sp1, sp2):
        if (
            isinstance(p1, (Iterable, SubPattern)) and
            isinstance(p2, (Iterable, SubPattern))
        ):
            if not equal_subpatterns(p1, p2):
                return False
        elif p1 != p2:
            return False
    return True


print(unescape(r'\{\"\ab(?:a|\Zc\{)'))
