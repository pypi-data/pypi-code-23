from collections import defaultdict

import jmespath

from .invocation_tools import _extract_invocations, _name_of


class VaqueroException(Exception):
    pass


def _make_pairs_table(d, sort_ks=True, depth=""):
    rows = [depth + "<table>"]
    ks = d.keys() if not sort_ks else sorted(d.keys())

    for k in ks:
        v = d[k]
        if isinstance(v, dict):
            v = _make_pairs_table(v, sort_ks=sort_ks, depth=depth + "\t")

        rows.append("<tr><td>{}</td><td>{}</td></tr>".format(k, v))

    rows.append("</table>")
    return "\n{}".format(depth).join(rows)


class Vaquero:

    def __init__(self, max_failures=None, capture_error_invocations=True,
                 annotate_failure_with_input=False):
        """
        :param max_failures: The maximum number of failures allowed before
            loudly signaling a problem. The default is None, which means the
            Vaquero object never raises an exception.

        :param capture_error_invocations: if True (default) captures errant
            invocations for post-processing. Otherwise, doesn't capture
            (useful for more production-oriented code)

        :param capture_error_invocations: if True (not default) then the
            captured invocation is annotated with a `top_input` field
            set to the input (as set by set_input)
        """
        self._max_failures = max_failures
        self._capture_error_invocations = capture_error_invocations
        self._annotate_failure_with_input = annotate_failure_with_input
        self._target_funcs = set()
        self.reset()

    def reset(self, turn_off_error_capturing=False):
        """
        Resets all internal counters and captured exceptions.

        :param turn_off_error_capturing:
        :return:
        """
        self._successes = 0
        self._failures = 0
        self._captures = defaultdict(list)
        self._last_input = None

        if turn_off_error_capturing is True:
            self._capture_error_invocations = False

    def stats(self):
        """
        :return: a dict with `successes`, `failures`, `ignored`, and
            `failures_by`
        """
        return {'successes': self._successes,
                'failures': self._failures,
                'ignored': 0,
                'failures_by': {k: len(v) for k, v in self._captures.items()}}

    @property
    def n_failures(self):
        return self._failures

    def merge(self, other):
        """
        Merge this Vaquero object with another.

        :param other: another vaquero object
        """
        self._successes += other._successes
        self._failures += other._failures

        for k, v in other._captures.items():
            if k in self._captures:
                self._captures[k].extend(v)
            else:
                self._captures[k] = v

    def stats_ignoring(self, *exc_types_to_ignore):
        """
        Works like `stats` but ignores some captured failures.

        :param exc_types_to_ignore: an arbitrary set of `exc_type`s to ignore.
        """
        exc_types_to_ignore = set([t.__name__ if hasattr(t, '__name__') else t
                                   for t in exc_types_to_ignore])

        n_ignored, n_failures, failures_by = 0, self._failures, {}
        for k, captures in self._captures.items():
            failures_by_k = 0
            for capture in captures:
                if capture['exc_type'] in exc_types_to_ignore:
                    n_failures -= 1
                    n_ignored += 1
                else:
                    failures_by_k += 1
            if failures_by_k > 0:
                failures_by[k] = failures_by_k

        return {'successes': self._successes,
                'ignored': n_ignored,
                'failures': n_failures,
                'failures_by': failures_by}

    def register_target(self, f):
        """
        Registers a function with the exception capturing machinery.

        :param f: a function (or string naming a function)
        """
        self._target_funcs.add(_name_of(f))

    def register_targets(self, target_funcs):
        """
        Register functions with the exception capturing machinery.

        :param target_funcs: a collection of functions or string names
        """
        for f in target_funcs:
            self.register_target(f)

    @property
    def target_funcs(self):
        return set(self._target_funcs)

    def set_input(self, input):
        """
        Set the input **prior** to using it.

        Useful for post failure analysis via the `last_input` property.
        """
        self._last_input = input

    def on_input(self, input):
        """
        Set the input **prior** to using it, then return the context.
        """
        self.set_input(input)
        return self

    @property
    def was_successful(self):
        return self._successes > 0 and self._failures == 0

    @property
    def last_input(self):
        return self._last_input

    def __enter__(self):
        return self.set_input

    def __exit__(self, exc_type, exc_value, tb):
        # TODO only catch certain types
        if exc_type is None:
            self._successes += 1
        elif exc_type == KeyboardInterrupt:
            return True  # Swallow exception. Programmer error!
        else:
            self._failures += 1

            # Gather invocations only for registered functions.
            invocations = [invoc for invoc in _extract_invocations(tb)
                           if invoc['name'] in self._target_funcs]
            if invocations:
                root_cause = invocations[-1]

                if self._capture_error_invocations:
                    if self._annotate_failure_with_input:
                        root_cause['top_input'] = self._last_input

                    # These are string-encoded for ease of JMES use.
                    root_cause['exc_type'] = exc_type.__name__
                    root_cause['exc_value'] = str(exc_value)

                    self._captures[root_cause['name']].append(root_cause)

                if self._failures > (self._max_failures or self._failures):
                    raise VaqueroException("Failure limit exceeded!")

                return True  # Swallow exception: see PEP-0343
            else:
                raise  # Exception in non-registered code. Don't swallow!

    def examine(self, f, selector=None, as_set=False):
        """
        Examine the exceptional cases for a given function.

        :param f: the function or name to examine
        :param selector: the JMES-based selector to apply to the captures
        :param as_set: if True return the selection result as a set. Only
            applies to examinations with a selector.
        :return: the invocations or a transformation of invocations
        """
        captures = self._captures[_name_of(f)]

        if selector is None:
            assert not as_set, "as_set=True only works with a selector"
            return captures
        else:
            items = jmespath.search(selector, captures)
            return set(items) if as_set else items

    def first_failure(self, f, ignore_call_args=False):
        errors = self.examine(f)
        assert errors, "No failure on {}".format(f)
        if ignore_call_args:
            return {k: v for k, v in errors[0].items() if k != 'call_args'}
        else:
            return errors[0]

    def execute_on_failure(self, f, i, captured_func_name=None):
        """
        Execute's f on some captured failure.

        :param f: a function that takes the captured invocation for its own
            name or the `captured_func_name` override
        :param i: the index of the capture for this function
        :param captured_func_name: override the name of the capture
        :return: the result of f(*captured_args)
        """
        name = captured_func_name or _name_of(f)
        if name not in self._captures:
            raise VaqueroException("Function `{}` has no issues".format(name))
        return f(*self._captures[name][i]['call_args'])

    def execute_over_failures(self, f, captured_func_name=None, *args, **kwargs):
        """
        Applies each set of failing arguments for f to a new vaquero object.

        :param f: the modified version of a registered callable
        :param captured_func_name: if specified, this is the captures to use
            for f, rather than inferring the name from f. It's useful if you
            want to experiment without overriding the original function
        :param args: passed to a new Vaquero object
        :param kwargs: passed to a new Vaquero object
        :return: the result of a Vaquero object capturing f(*args_in_failure)
        """
        name = captured_func_name or _name_of(f)
        if name not in self._captures:
            raise VaqueroException("Function `{}` has no issues".format(name))

        sub_vaquero = Vaquero(*args, **kwargs)
        sub_vaquero.register_target(f)

        for capture in self._captures[name]:
            args = capture['call_args']
            with sub_vaquero:
                f(*args)

        return sub_vaquero

    def _repr_html_(self):
        return _make_pairs_table(self.stats())
