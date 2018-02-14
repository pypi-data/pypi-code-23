from fnmatch import translate

from polymatch.matchers.regex import RegexMatcher


class GlobMatcher(RegexMatcher):
    def compile_pattern(self, raw_pattern, flags=0):
        if isinstance(raw_pattern, bytes):
            # Mimic how fnmatch handles bytes patterns
            pat_str = str(raw_pattern, 'ISO-8859-1')
            res_str = translate(pat_str)
            res = bytes(res_str, 'ISO-8859-1')
        else:
            res = translate(raw_pattern)

        return super().compile_pattern(res, flags)

    @classmethod
    def get_type(cls):
        return "glob"
