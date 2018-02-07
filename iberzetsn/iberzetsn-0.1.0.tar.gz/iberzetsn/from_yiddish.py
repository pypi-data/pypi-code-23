from .letters import YIDDISH_LETTER_LOOKUP, YIDDISH_PREFIX_LOOKUP
from .letters import YIDDISH_WORD_LOOKUP


def yiddish_to_roman(s):
    if not s:
        return ""
    if " " in s:
        words = s.split(" ")
        return " ".join(yiddish_to_roman(w) for w in words)
    if s in YIDDISH_WORD_LOOKUP:
        return YIDDISH_WORD_LOOKUP[s]
    return _yiddish_to_roman_simple_word(s)


def _yiddish_to_roman_simple_word(s):
    for y in YIDDISH_PREFIX_LOOKUP:
        if s.startswith(y):
            ss = s[len(y):]
            return YIDDISH_PREFIX_LOOKUP[y] + yiddish_to_roman(ss)
    r = []
    b = ""
    for c in s:
        if c in YIDDISH_LETTER_LOOKUP:
            r.append(YIDDISH_LETTER_LOOKUP[c])
        elif b + c in YIDDISH_LETTER_LOOKUP:
            r.append(YIDDISH_LETTER_LOOKUP[b + c])
        else:
            b = c
    return "".join(r)
