#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Detect and manipulate references to variables.

The variable syntax is defined by the arguments to `build_varre`.

.. autodata:: REGEXPS

"""

from __future__ import print_function
from __future__ import absolute_import

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2008-2018, Lluís Vilanova"
__license__ = "GPL version 3 or later"

__maintainer__ = "Lluís Vilanova"
__email__ = "llvilanovag@gmail.com"


import abc
import collections
import functools
import re
import six

from . import utils


# Base functionality

#: Dictionary mapping the "name" of a variable referencing syntax, to the
#: definition of how to detect such references.
#:
#: The values on the dictionary must contain a 3-element tuple:
#:  * Prefix enclosing the variable name.
#:  * Regular expression for the variable name.
#:  * Postfix enclosing the variable name.
REGEXPS = {
    # <variable start str>, <variable name regexp>, <variable end str>
    "@": ("@", "[^@]+", "@"),
    "$": ("$(", "[^)]+", ")"),
    }


def _parts2varre(parts, ignore=None):
    """Build a regexp to match variable names."""
    if len(parts) != 3:
        raise ValueError("Variable regexp with invalid number of " +
                         "parts: " + str(parts))
    prefix = "".join(["\\" + char for char in parts[0]])
    prefix = prefix + "(?<!\\\\" + prefix + ")"
    varname = parts[1]
    postfix = "".join(["\\" + char for char in parts[2]])
    postfix = postfix + "(?<!" + postfix[:-1] + "\\\\" + postfix[-1:] + ")"
    if ignore is None:
        return prefix + "(" + varname + ")" + postfix
    else:
        assert isinstance(ignore, collections.Iterable) and \
            not isinstance(ignore, six.string_types)
        # negative lookbehind of ignores
        ignore_behind = ["(?<!%s%s)" % (prefix, elem) for elem in ignore]
        ignore_behind = "".join(ignore_behind)
        # negative lookahead of ignores
        ignore_ahead = "(?!" + (postfix + "|").join(ignore) + postfix + ")"
        # <not preceeded by ignores><prefix>(<not an ignore><varname>)<postfix>
        return ignore_behind + prefix + \
            "(" + ignore_ahead + varname + ")" + \
            postfix

_CREGEXPS = dict([(key, re.compile(_parts2varre(val)))
                  for key, val in REGEXPS.items()])


def build_varre(name, ignore=None):
    """Build a compiled regexp for intentifying variables.

    Parameters
    ----------
    name : str or tuple
        Either a key in :data:`REGEXPS` for a pre-existing named variable
        syntax, or the corresponding 3-element tuple.
    ignore : list(str), optional
        Sequence of variable names that must be ignored when searching for
        variable references.

    Returns
    -------
    tuple
        A 2-element tuple with the 3-element tuple (useful in case `name`
        referenced a key in :data:`REGEXPS`) and the compiled regexp for
        identifying such variable references.
    """
    varre = None
    cvarre = None
    if name in REGEXPS:
        parts = REGEXPS[name]
        if ignore is None:
            cvarre = _CREGEXPS[name]
        else:
            cvarre = re.compile(_parts2varre(parts, ignore))
    else:
        parts = name
        varre = _parts2varre(parts, ignore)
        cvarre = re.compile(varre)
    return parts, cvarre


def expr_to_regexp(varre, expr, contents=".+"):
    """Convert variable references into a regular expression with named groups.

    Parameters
    ----------
    varre
        A valid argument to `build_varre`.
    expr : str
        Expression to transform.
    contents : str, optional
        Regular expression for named group contents.

    """
    variables = set()
    res = ""
    for isvar, text in Tokenizer(varre).tokenize(expr):
        if isvar:
            if text in variables:
                res += "(?P=%s)" % text
            else:
                res += "(?P<%s>%s)" % (text, contents)
                variables.add(text)
        else:
            res += text
    return res


def regexp_get_names(regexp):
    """Get a list of the group names in a regular expression."""
    cre = re.compile(regexp)
    return [k for v, k in sorted(
        [(v, k)
         for k, v in six.iteritems(cre.groupindex)]
    )]


def expr_get_vars(varre, expr, accept_regexp=False):
    """Get a list with the variable names present in given expression.

    Parameters
    ----------
    varre
        A valid argument to `build_varre`.
    expr : str
        Expression to transform.
    accept_regexp : bool, optional
        Whether to accept a mix of variable references and regexp named groups.

    """
    if accept_regexp:
        return regexp_get_names(expr_to_regexp(varre, expr))
    else:
        res = []
        variables = set()
        for var in Tokenizer(varre).vars(expr):
            if var not in variables:
                variables.add(var)
                res.append(var)
        return res


class Tokenizer (six.with_metaclass(utils.SelectiveClassMemoize)):
    """Split a string at variable reference boundaries."""

    def __init__(self, varre, ignore=None):
        """
        Parameters
        ----------
        varre
            A valid argument to `build_varre`.
        ignore : list(str), optional
            Variable names to ignore during tokenization.
        """
        (self.var_start, _, self.var_end), self._cre = build_varre(
            varre, ignore)

    def tokenize(self, source):
        """Generator to tokenize a string.

        Generates a sequence of ``(is_variable, token_text)`` pairs.

        The tokenized variables names are stripped off of their prefix and
        postfix variable reference syntax.

        Notes
        -----
        `source` is automatically stringified to provide transparency with
        non-string inputs.
        """
        if not isinstance(source, six.string_types):
            text = str(source)
        else:
            text = source
        tokens = self._cre.split(text)
        if len(tokens) > 0 and tokens[0] == "":
            isvar = True
            tokens = tokens[1:]
        else:
            isvar = False
        for tok in tokens:
            yield (isvar, tok)
            isvar = not isvar

    def vars(self, source):
        """Generator to extract only variable names from a string."""
        for tok in self.tokenize(source):
            if tok[0]:
                yield tok[1]

Tokenizer.memoize_new("@")
Tokenizer.memoize_new("@", None)
Tokenizer.memoize_new("@", set())
Tokenizer.memoize_new("$")
Tokenizer.memoize_new("$", None)
Tokenizer.memoize_new("$", set())


# Variable translators

class XlateError (Exception):
    """Reference to unknown variable."""
    def __init__(self, variables, source, current, subst):
        self.variables = variables
        self.source = source
        self.current = current
        self.subst = subst

    def __str__(self):
        msg = ["Missing translation(s) for: %s" % ", ".join(self.variables),
               "Original source text: '%s'" % self.source]
        if self.current is not None:
            msg.append("Current text: '%s'" % self.current)
        if self.subst is not None:
            msg.append("Offending substitution: %s" % self.subst)
        return "\n".join(msg)


class RecursiveError (Exception):
    """Recursive variable translation."""
    def __init__(self, variables, source):
        self.variables = variables
        self.source = source

    def __str__(self):
        msg = ["Possible recursive translation for: %s" %
               ", ".join(self.variables),
               "Original source text: '%s'" % self.source]
        return "\n".join(msg)


class _XlatorMetaclass (utils.SelectiveClassMemoize, abc.ABCMeta):
    pass


class Xlator (six.with_metaclass(_XlatorMetaclass)):
    """Generic class for translating references to variables into values."""

    def __init__(self, varre, ignore=None):
        """
        Parameters
        ----------
        varre
            A valid argument to `build_varre`.
        ignore : list(str), optional
            Variable names to ignore during translation.
        """
        (self.var_start, _, self.var_end), self._cre = build_varre(
            varre, ignore)
        self._varre = varre

    @abc.abstractmethod
    def _xlate(self, source, subst):
        pass

    def xlate(self, source, subst=None, allow_unxlated=False):
        """Translate a string with the given dict.

        Parameters
        ----------
        source : str
            String with variable references.
        subst
            The definition of translations to apply.
            The interpretation of this argument depends on the specific
            subclass.
        allow_unxlated : bool, optional
            Allow for some variable references to remain untranslated if they
            are not in `subst` (otherwise raise an exception).

        Returns
        -------
        str
            String with all variable references replaced with the contents of
            `subst`.

        Notes
        -----
        If `source` is not a string, simply returns it with no translations
        applied.
        """
        # TODO: this is extremely hackish, as we account for the "special"
        #       value in PrepDictXlator
        if source is not None and not isinstance(source, str):
            return source

        text = source
        res, unxlated = self._xlate(text, subst)

        if not allow_unxlated and unxlated is not None:
            raise XlateError(unxlated, source, None, subst)
        return res

    def xlate_rec(self, source, subst=None, allow_unxlated=False):
        """Recursively apply `xlate`."""
        if not isinstance(source, six.string_types):
            return source

        tries = 0
        text = source
        prev = None
        while prev != text:
            prev = text
            text, unxlated = self._xlate(text, subst)

            # For the sake of performance, do not check real recursion but
            # instead look for a "long enough" loop
            if tries > 100:
                tokenizer = Tokenizer(self._varre)
                variables = list(tokenizer.vars(text))
                raise RecursiveError(variables, source)
            tries += 1

        if not allow_unxlated and unxlated is not None:
            raise XlateError(unxlated, source, prev, subst)
        return text


class NullXlator (Xlator):
    """Eliminate variable references from a string.

    Argument `subst` in `xlate` must be ``None``.
    """
    def _xlate(self, source, subst=None):
        assert subst is None
        return self._cre.sub("", str(source)), None

NullXlator.memoize_new("@")
NullXlator.memoize_new("@", None)
NullXlator.memoize_new("@", set())
NullXlator.memoize_new("$")
NullXlator.memoize_new("$", None)
NullXlator.memoize_new("$", set())


class ConstXlator (Xlator):
    """Translate all variable references with a constant string.

    Argument `subst` in `xlate` must be a string.
    """
    def _xlate(self, source, subst):
        assert isinstance(subst, six.string_types)
        return self._cre.sub(subst, str(source)), None

ConstXlator.memoize_new("@")
ConstXlator.memoize_new("@", None)
ConstXlator.memoize_new("@", set())
ConstXlator.memoize_new("$")
ConstXlator.memoize_new("$", None)
ConstXlator.memoize_new("$", set())


class ListXlator (Xlator):
    """Substitute the N'th variable with the N'th value in a sequence.

    Argument `subst` in `xlate` must be a list.
    """

    @functools.wraps(Xlator.__init__)
    def __init__(self, varre, ignore=None):
        self._tokenizer = Tokenizer(varre, ignore)

    def _xlate(self, source, subst):
        assert isinstance(subst, collections.Iterable) and \
            not isinstance(subst, six.string_types)
        res = ""
        idx = 0
        unxlated = []
        for tok in self._tokenizer.tokenize(source):
            if tok[0]:
                if idx >= len(subst):
                    unxlated.append(tok[1])
                else:
                    res += subst[idx]
                    idx += 1
            else:
                res += tok[1]
        if len(unxlated) is 0:
            unxlated = None
        return res, unxlated

ListXlator.memoize_new("@")
ListXlator.memoize_new("@", None)
ListXlator.memoize_new("@", set())
ListXlator.memoize_new("$")
ListXlator.memoize_new("$", None)
ListXlator.memoize_new("$", set())


class DictXlator (Xlator):
    """Substitute variable references with a dictionary mapping variable names
    to substitution values.

    Argument `subst` in `xlate` must be a dict-like object.
    """

    @functools.wraps(Xlator.__init__)
    def __init__(self, varre, ignore=None):
        Xlator.__init__(self, varre, ignore)
        self._tokenizer = Tokenizer(varre, ignore)

    def _xlate(self, source, subst):
        if not isinstance(subst, dict):
            raise TypeError("Tried to use a DictXlator "
                            "with a bad substitution type: '%s'" % subst)

        unxlated = []
        res = ""
        for isvar, tok in self._tokenizer.tokenize(source):
            if isvar:
                if tok in subst:
                    val = subst[tok]
                    if isinstance(val, six.string_types):
                        res += val
                    else:
                        res += str(val)
                else:
                    unxlated.append(tok)
                    res += self.var_start + tok + self.var_end
            else:
                res += tok
        if len(unxlated) is 0:
            unxlated = None
        return res, unxlated

DictXlator.memoize_new("@")
DictXlator.memoize_new("@", None)
DictXlator.memoize_new("@", set())
DictXlator.memoize_new("$")
DictXlator.memoize_new("$", None)
DictXlator.memoize_new("$", set())


class PrepDictXlator (DictXlator):
    """A `DictXlator` optimized for repeated substitutions on the same string.

    If argument `source` in `xlate` is ``None``, uses the source
    identified by a previous call to `prepare`. Otherwise, falls back to
    the `DictXlator` behaviour.

    Argument `subst` in `xlate` must be a dictionary.
    """
    @functools.wraps(Xlator.__init__)
    def __init__(self, varre, ignore=None):
        DictXlator.__init__(self, varre, ignore)
        self._prepared = None

    def prepare(self, source):
        """Prepare to start translating the given string."""
        self._prepared = self._cre.sub(r"%(\1)s", source)
        self._dict = dict(
            [(var, "%s%s%s" % (self.var_start, var, self.var_end))
             for var in self._tokenizer.vars(source)])
        self._keys = set(six.iterkeys(self._dict))

    def _xlate(self, source, subst):
        if source is not None:
            return DictXlator._xlate(self, source, subst)
        else:
            sdict = self._dict.copy()
            keys = set()
            for key, val in six.iteritems(subst):
                if key in sdict:
                    sdict[key] = val
                    keys.add(key)
            unxlated = self._keys - keys
            if len(unxlated) is 0:
                unxlated = None
            return self._prepared % sdict, unxlated
