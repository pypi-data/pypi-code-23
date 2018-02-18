from polymatch import PolymorphicMatcher

try:
    import regex
except ImportError:
    regex = None

    import re

    IGNORECASE = re.IGNORECASE
else:
    IGNORECASE = regex.IGNORECASE


class RegexMatcher(PolymorphicMatcher):
    def compile_pattern(self, raw_pattern, flags=0):
        if regex:
            return regex.compile(raw_pattern, flags)

        return re.compile(raw_pattern, flags)

    def compile_pattern_cs(self, raw_pattern):
        return self.compile_pattern(raw_pattern)

    def compile_pattern_ci(self, raw_pattern):
        return self.compile_pattern(raw_pattern, IGNORECASE)

    def compile_pattern_cf(self, raw_pattern):
        if not regex:
            raise NotImplementedError

        return self.compile_pattern(raw_pattern, regex.FULLCASE | IGNORECASE)

    def match_text(self, pattern, text):
        return bool(pattern.match(text))

    def match_text_cf(self, pattern, text):
        if not regex:
            raise NotImplementedError

        return self.match_text(pattern, text)

    def match_text_ci(self, pattern, text):
        return self.match_text(pattern, text)

    def match_text_cs(self, pattern, text):
        return self.match_text(pattern, text)

    @classmethod
    def get_type(cls):
        return "regex"
