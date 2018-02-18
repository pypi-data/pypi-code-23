from abc import ABCMeta, abstractmethod
from enum import Enum

import polymatch
from polymatch.error import PatternCompileError, PatternNotCompiledError, PatternTextTypeMismatchError


class CaseAction(Enum):
    NONE = 'none', ''  # Use whatever the pattern's default is
    CASESENSITIVE = 'case-sensitive', 'cs'  # Fore case sensitivity
    CASEINSENSITIVE = 'case-insensitive', 'ci'  # Force case insensitivity
    CASEFOLD = 'casefold', 'cf'  # Force case-folded comparison


class PolymorphicMatcher(metaclass=ABCMeta):
    _empty = object()

    def __init__(self, pattern, case_action=CaseAction.NONE, invert=False):
        self._raw_pattern = pattern
        self._str_type = type(pattern)
        self._compiled_pattern = self._empty
        self._case_action = case_action
        self._invert = invert

        self._compile_func, self._match_func = self._get_case_functions()

        if self._case_action is CaseAction.CASEFOLD and self._str_type is bytes:
            raise TypeError("Case-folding is not supported with bytes patterns")

    def try_compile(self):
        try:
            self.compile()
        except PatternCompileError:
            return False

        return True

    def compile(self):
        try:
            self._compiled_pattern = self._compile_func(self._raw_pattern)
        except Exception as e:
            raise PatternCompileError("Failed to compile pattern {!r}".format(self._raw_pattern)) from e

    def __eq__(self, other):
        if isinstance(other, self._str_type):
            return self.match(other)

        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self._str_type):
            return not self.match(other)

        return NotImplemented

    def match(self, text):
        if not isinstance(text, self._str_type):
            raise PatternTextTypeMismatchError(self._str_type, type(text))

        if not self.is_compiled():
            # If it wasn't compiled
            raise PatternNotCompiledError("Pattern must be compiled.")

        out = self._match_func(self._compiled_pattern, text)

        if self._invert:
            return not out

        return out

    def is_compiled(self):
        return self._compiled_pattern is not self._empty

    @abstractmethod
    def compile_pattern(self, raw_pattern):
        raise NotImplementedError

    @abstractmethod
    def compile_pattern_cs(self, raw_pattern):
        """Matchers should override this to compile their pattern with case-sensitive options"""
        raise NotImplementedError

    @abstractmethod
    def compile_pattern_ci(self, raw_pattern):
        """Matchers should override this to compile their pattern with case-insensitive options"""
        raise NotImplementedError

    @abstractmethod
    def compile_pattern_cf(self, raw_pattern):
        """Matchers should override this to compile their pattern with case-folding options"""
        raise NotImplementedError

    @abstractmethod
    def match_text(self, pattern, text):
        raise NotImplementedError

    def match_text_cs(self, pattern, text):
        return self.match_text(pattern, text)

    def match_text_ci(self, pattern, text):
        return self.match_text(pattern, text.lower())

    def match_text_cf(self, pattern, text):
        return self.match_text(pattern, text.casefold())

    def _get_case_functions(self):
        suffix = self._case_action.value[1]

        if suffix:
            suffix = '_' + suffix

        return getattr(self, "compile_pattern" + suffix), getattr(self, "match_text" + suffix)

    @classmethod
    @abstractmethod
    def get_type(cls):
        raise NotImplementedError

    @property
    def pattern(self):
        return self._raw_pattern

    @property
    def case_action(self):
        return self._case_action

    @property
    def inverted(self):
        return self._invert

    def __str__(self):
        return "{}{}:{}:{}".format(
            '~' if self._invert else '', self.get_type(), self._case_action.value[1], self._raw_pattern
        )

    def __repr__(self):
        return "{}(pattern={!r}, case_action={!r}, invert={!r})".format(
            type(self).__name__, self._raw_pattern, self._case_action, self._invert
        )

    def __getstate__(self):
        return polymatch.__version__, self._raw_pattern, self._case_action, self._invert, self._compiled_pattern, \
               self._str_type, self._empty

    def __setstate__(self, state):
        if len(state) > 6:
            version, *state = state
        else:
            version = (0, 0, 0)

        self._raw_pattern, self._case_action, self._invert, self._compiled_pattern, self._str_type, self._empty = state
        self._compile_func, self._match_func = self._get_case_functions()

        if version != polymatch.__version__ and self.is_compiled():
            self.compile()
