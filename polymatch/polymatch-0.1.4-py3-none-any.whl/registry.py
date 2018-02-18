from collections import OrderedDict

from polymatch.base import PolymorphicMatcher, CaseAction
from polymatch.error import DuplicateMatcherRegistrationError, NoSuchMatcherError, NoMatchersAvailable
from polymatch.matchers.glob import GlobMatcher
from polymatch.matchers.regex import RegexMatcher
from polymatch.matchers.standard import ExactMatcher, ContainsMatcher


def _opt_split(text, delim=':', empty="", invchar='~'):
    if text.startswith(invchar):
        invert = True
        text = text[len(invchar):]
    else:
        invert = False

    if delim in text:
        name, _, text = text.partition(delim)

        if delim in text:
            opts, _, text = text.partition(delim)
        else:
            opts = empty
    else:
        name = empty
        opts = empty

    return invert, name, opts, text


def _parse_pattern_string(text):
    if isinstance(text, str):
        invert, name, opts, pattern = _opt_split(text)

        return invert, name, opts, pattern
    elif isinstance(text, bytes):
        invert, name, opts, pattern = _opt_split(text, b':', b'', b'~')
        return invert, name.decode(), opts.decode(), pattern
    else:
        raise TypeError("Unable to parse pattern string of type {!r}".format(type(text).__name__))


class PatternMatcherRegistry:
    def __init__(self):
        self._matchers = OrderedDict()

    def register(self, cls):
        name = cls.get_type()
        if name in self._matchers:
            raise DuplicateMatcherRegistrationError(name)

        if not issubclass(cls, PolymorphicMatcher):
            raise TypeError(
                "Pattern matcher must be of type {!r} not {!r}".format(PolymorphicMatcher.__name__, cls.__name__)
            )

        self._matchers[name] = cls

    def remove(self, name):
        del self._matchers[name]

    def __getitem__(self, item):
        return self.get_matcher(item)

    def get_matcher(self, name):
        try:
            return self._matchers[name]
        except LookupError as e:
            raise NoSuchMatcherError(name) from e

    def get_default_matcher(self):
        if self._matchers:
            return list(self._matchers.values())[0]
        else:
            raise NoMatchersAvailable()

    def pattern_from_string(self, text):
        invert, name, opts, pattern = _parse_pattern_string(text)
        if not name:
            match_cls = self.get_default_matcher()
        else:
            match_cls = self.get_matcher(name)

        case_action = None
        for action in CaseAction:
            if action.value[1] == opts:
                case_action = action
                break

        if case_action is None:
            raise LookupError("Unable to find CaseAction for options: {!r}".format(opts))

        return match_cls(pattern, case_action, invert)


pattern_registry = PatternMatcherRegistry()

pattern_registry.register(ExactMatcher)
pattern_registry.register(ContainsMatcher)
pattern_registry.register(GlobMatcher)
pattern_registry.register(RegexMatcher)
