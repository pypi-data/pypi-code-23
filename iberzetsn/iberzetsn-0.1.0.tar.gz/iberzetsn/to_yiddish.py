from .letters import ROMAN_FINAL_LOOKUP, ROMAN_LOOKUP


def roman_to_yiddish(s):
    if not s:
        return ""
    if " " in s:
        words = s.split(" ")
        return " ".join(roman_to_yiddish(w) for w in words)
    if len(s) == 1 and s in ROMAN_FINAL_LOOKUP:
        return ROMAN_FINAL_LOOKUP[s]
    prefixes = [ x for x in ROMAN_LOOKUP if s.startswith(x) ]
    if prefixes:
        prefixes.sort(key=len)
        x = prefixes[-1]
        return ROMAN_LOOKUP[x] + roman_to_yiddish(s[len(x):])
    raise ValueError("Couldn't find the first Yiddish character of %s" % (s, ))
