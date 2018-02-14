from polymatch import PolymorphicMatcher


class ExactMatcher(PolymorphicMatcher):
    def compile_pattern(self, raw_pattern):
        return raw_pattern

    def compile_pattern_cs(self, raw_pattern):
        return raw_pattern

    def compile_pattern_ci(self, raw_pattern):
        return raw_pattern.lower()

    def compile_pattern_cf(self, raw_pattern):
        return raw_pattern.casefold()

    def match_text(self, pattern, text):
        return text == pattern

    @classmethod
    def get_type(cls):
        return "exact"


class ContainsMatcher(PolymorphicMatcher):
    def compile_pattern(self, raw_pattern):
        return raw_pattern

    def compile_pattern_cs(self, raw_pattern):
        return raw_pattern

    def compile_pattern_ci(self, raw_pattern):
        return raw_pattern.lower()

    def compile_pattern_cf(self, raw_pattern):
        return raw_pattern.casefold()

    def match_text(self, pattern, text):
        return text in pattern

    @classmethod
    def get_type(cls):
        return "contains"
