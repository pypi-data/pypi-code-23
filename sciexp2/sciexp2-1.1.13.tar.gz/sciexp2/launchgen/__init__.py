#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Automate generation of parametrized launchers."""

from __future__ import print_function
from __future__ import absolute_import

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2008-2018, Lluís Vilanova"
__license__ = "GPL version 3 or later"

__maintainer__ = "Lluís Vilanova"
__email__ = "llvilanovag@gmail.com"


import collections
import contextlib
import functools
import operator
import os
import shutil
import six
import warnings

from sciexp2.common import parallel as parallel_pkg
from sciexp2.common import progress
from sciexp2.common import utils
from sciexp2.common import varref
import sciexp2.common.instance
import sciexp2.common.filter
from sciexp2.common.utils import execute_with_sigint
from sciexp2.common import pp
from sciexp2 import templates
from sciexp2 import launcher


_LISTXLATOR = varref.ListXlator("@")
_DICTXLATOR = varref.DictXlator("@")
_EXPANDER = sciexp2.common.instance.Expander("@")


######################################################################
# Helper functions

def file_contents(path, mode="r"):
    """Return the contents of given path as a string.

    Can be used as an argument to any method in `Launchgen` that accepts an
    expression. If the path itself is an expression, the appropriate file will
    be read after expanding its path expression.

    """
    variables = varref.expr_get_vars("@", path)

    def read_file(path, mode):
        with open(path, mode) as f:
            return "".join(f.readlines())

    if len(variables) == 0:
        return read_file(path, mode)

    def deferred_read_file(*values):
        real_path = _LISTXLATOR.xlate(path, [str(v) for v in values])
        return read_file(real_path, mode)

    return defer(deferred_read_file, *[defer(v) for v in variables])


######################################################################
# Partial views (function identification)

VIEW_SUPPORTED = {}


def _supports_view(other):
    assert callable(other)

    def _func_decorator(func):
        assert callable(func)
        assert func not in VIEW_SUPPORTED
        VIEW_SUPPORTED[func.__name__] = other.__name__
        return func

    return _func_decorator


######################################################################
# Launchgen

class Launchgen (pp.Pretty):
    """Define and generate program launchers.

    Parameters
    ----------
    contents : optional
        Initial contents.
    out : optional
        Initial value for the `out` attribute.
    dereference : bool, optional
        Initial value for the `dereference` attribute.

    Attributes
    ----------
    out : str
        Output directory for all non-absolute paths.
    contents : `~sciexp2.common.instance.InstanceGroup`
        Instances describing the elements of this dimension.

    See also
    --------
    file_contents

    """

    #: Output directory for all non-absolute paths.
    out = "./out"

    #: Whether to dereference source symlinks during pack.
    dereference = False

    def __init__(self, contents=None, **kwargs):
        out = kwargs.pop("out", None)
        dereference = kwargs.pop("dereference", None)
        utils.assert_kwargs(kwargs)

        if contents is None:
            contents = sciexp2.common.instance.InstanceGroup()
            # add dummy contents
            contents += sciexp2.common.instance.Instance()
        if isinstance(contents, Launchgen) or\
           isinstance(contents, LaunchgenView):
            if dereference is None:
                dereference = contents.dereference
            if out is None:
                out = contents.out
            contents = contents.contents
        if out is not None:
            self.out = out
        if dereference is not None:
            self.dereference = dereference

        self._contents = sciexp2.common.instance.InstanceGroup(contents)

        self._deferred = set()

    @property
    def contents(self):
        """Instances describing the elements of this dimension."""
        return self._contents

    def _do_repr_pretty_(self, select, p, cycle):
        if select is None:
            select = sciexp2.common.filter.Filter()
        with self.pformat(p, cycle):
            if len(list(self._contents.variables())) > 0:
                p.pretty(list(self._contents.select(select)))
                p.text(",")
                p.breakable()
            p.text("out=%r" % self.out)

    @_supports_view(_do_repr_pretty_)
    def _repr_pretty_(self, p, cycle):
        self._do_repr_pretty_(None, p, cycle)

    def select(self, *filters):
        """Get a `LaunchgenView` to operate on the subset matching `filters`.

        Notes
        -----
        The relative order inside `contents` between new and old instances is
        mantained, such that the result appears as if instances matching the
        filters were "expanded" in-place.

        Examples
        --------
        All operations are performed only on selected elements:

        >>> l = Launchgen()
        >>> l.params(a=range(2), b=range(2))
        >>> l
        Launchgen([Instance({'a': 0, 'b': 0}),
                   Instance({'a': 0, 'b': 1}),
                   Instance({'a': 1, 'b': 0}),
                   Instance({'a': 1, 'b': 1})],
                  out='./out')
        >>> v = l.select("a == b")
        >>> v.params(c=(defer("a") + defer("b")))
        >>> v
        Launchgen([Instance({'a': 0, 'b': 0, 'c': 0}),
                   Instance({'a': 1, 'b': 1, 'c': 2})],
                  out='./out')

        And appear on the original object as if they happened "in-place":

        >>> l
        Launchgen([Instance({'a': 0, 'b': 0, 'c': 0}),
                   Instance({'a': 0, 'b': 1}),
                   Instance({'a': 1, 'b': 0}),
                   Instance({'a': 1, 'b': 1, 'c': 2})],
                  out='./out')

        The inverse selection is also readily available:

        >>> i = v.select_inverse()
        >>> i
        Launchgen([Instance({'a': 0, 'b': 1}), Instance({'a': 1, 'b': 0})],
                  out='./out')
        >>> i.params(d=(defer("a") * defer("b")))
        >>> l
        Launchgen([Instance({'a': 0, 'b': 0, 'c': 0}),
                   Instance({'a': 0, 'b': 1, 'd': 0}),
                   Instance({'a': 1, 'b': 0, 'd': 0}),
                   Instance({'a': 1, 'b': 1, 'c': 2})],
                  out='./out')

        As well as nested selections are also supported:

        >>> n = v.select("c == 0")
        >>> n.params(e=[10, 20])
        >>> n.select_inverse().params(e=[30, 40])
        >>> l
        Launchgen([Instance({'a': 0, 'b': 0, 'c': 0, 'e': 10}),
                   Instance({'a': 0, 'b': 0, 'c': 0, 'e': 20}),
                   Instance({'a': 0, 'b': 1, 'd': 0}),
                   Instance({'a': 1, 'b': 0, 'd': 0}),
                   Instance({'a': 1, 'b': 1, 'c': 2, 'e': 30}),
                   Instance({'a': 1, 'b': 1, 'c': 2, 'e': 40})],
                  out='./out')

        """
        return LaunchgenView(self,
                             sciexp2.common.filter.Filter("True"),
                             sciexp2.common.filter.Filter(*filters))

    #: Default standard input for `execute`
    STDIN = None
    #: Default standard output for `execute`
    STDOUT = None
    #: Default standard error for `execute`
    STDERR = None

    def _execute(self, select, *args, **kwargs):
        parallel = kwargs.pop("parallel", None)
        std_args = {
            'stdin':  kwargs.pop("stdin",  self.STDIN),
            'stdout': kwargs.pop("stdout", self.STDOUT),
            'stderr': kwargs.pop("stderr", self.STDERR),
        }
        utils.assert_kwargs(kwargs)

        def std_needs_translate(name):
            arg = std_args[name]
            return isinstance(arg, six.string_types) and \
                varref.expr_get_vars("@", arg, accept_regexp=True)
        std_vars = {
            'stdin':  std_needs_translate('stdin'),
            'stdout': std_needs_translate('stdout'),
            'stderr': std_needs_translate('stderr'),
        }

        if len(args) == 0:
            return

        cmd_arg_sep = "|;|"
        cmd = cmd_arg_sep.join(args)

        expansions = _EXPANDER.expand(cmd, self._contents,
                                      filter_=select,
                                      recursive=True)

        @contextlib.contextmanager
        def get_stdfile_null():
            yield None

        def get_stdfile(name, expansion):
            arg = std_args[name]
            if std_vars[name]:
                instance = expansion.instances.get_index(0)
                path = utils.get_path(_DICTXLATOR.xlate_rec(arg,
                                                            instance))
                return open(path, "w")
            elif isinstance(arg, six.string_types):
                path = utils.get_path(arg)
                return open(path, "w")
            elif arg is None:
                return get_stdfile_null()
            else:
                return arg

        def do_execute(ecmd):
            real_cmd = ecmd.text
            if len(args) == 1:
                progress.verbose(real_cmd)
                real_cmd = [real_cmd]
            else:
                real_cmd = [real_cmd.split(cmd_arg_sep)]
                progress.verbose(" ".join(real_cmd[0]))

            with get_stdfile("stdin",  ecmd) as stdin,\
                 get_stdfile("stdout", ecmd) as stdout,\
                 get_stdfile("stderr", ecmd) as stderr:
                res = execute_with_sigint(
                    *real_cmd,
                    shell=len(args) == 1,
                    stdin=stdin,
                    stdout=stdout,
                    stderr=stderr)
            if res != 0:
                raise Exception("Command did not finish correctly: "
                                "%s -> %d" % (" ".join(real_cmd[0]), res))

        with progress.get(expansions, msg="Executing commands...") as progr:
            if parallel is False:
                for ecmd in six.itervalues(expansions):
                    do_execute(ecmd)
                    progr()
            else:
                if parallel is True:
                    parallel = None
                work = list(six.itervalues(expansions))
                for i in parallel_pkg.t_imap_unordered(
                        work, do_execute, parallelism=parallel):
                    progr()

    @_supports_view(_execute)
    def execute(self, *args, **kwargs):
        """Execute an external program of shell command.

        If a single string is passed, it's interpreted as an expression that is
        expanded and then executed as a shell command.

        A list of strings is interpreted as a program name and its list of
        arguments (all treated as expressions and expanded).

        Parameters
        ----------
        args : str or list of str
            Command to execute.
        stdin, stdout, stderr : file or str, optional
            Paths for the standard input/output/error for the command (defaults
            to `STDIN`/`STDOUT`/`STDERR`).
        parallel : optional
            Whether to execute commands in parallel using separate processes
            (default is `False`).

        Notes
        -----
        If strings are used for `stdin`, `stdout` or `stderr`, these are
        treated as expressions and, thus, are translated accordingly.

        Command execution is internally handled by `subproces.Popen` and thus
        the `stdin`, `stdout` and `stderr` arguments can also have any value
        accepted by it.

        See also
        --------
        sciexp2.common.parallel.get_parallelism

        """
        self._execute(None, *args, **kwargs)

    #: Variables added by `_find_files_generic`
    _find_files_generic__VARS = set(["FILE"])

    def _find_files_generic(self, select, expression, filters,
                            variables, progr_msg,
                            process=None):
        if process is None:
            def generic_process(instance):
                yield instance
            process = generic_process

        if select is not None:
            selected_indexes = [idx for idx, i in enumerate(self._contents)
                                if select.match(i)]
            if len(selected_indexes) == 0:
                contents = sciexp2.common.instance.InstanceGroup(
                    self._contents)
                contents_rest = sciexp2.common.instance.InstanceGroup()
            else:
                last = max(selected_indexes)
                contents = sciexp2.common.instance.InstanceGroup(
                    self._contents.get_index(slice(0, last+1)))
                contents_rest = sciexp2.common.instance.InstanceGroup(
                    self._contents.get_index(slice(last+1, -1)))
        else:
            contents = sciexp2.common.instance.InstanceGroup(self._contents)
            contents_rest = sciexp2.common.instance.InstanceGroup()

        # take care of dummy contents
        if len(contents) is 1 and len(list(contents.variables())) is 0:
            contents = sciexp2.common.instance.InstanceGroup()

        filters = sciexp2.common.filter.Filter(*filters)
        fvariables = set(varref.expr_get_vars("@", expression, True)) |\
                     self._find_files_generic__VARS | variables
        filters.validate(fvariables)

        files = utils.find_files("@", expression, "FILE")
        with progress.progressable_simple(
                files, None, msg=progr_msg) as pfiles:
            for instance in pfiles:
                for instance in process(instance):
                    if filters.match(instance):
                        contents.add(instance)

        contents = contents + contents_rest

        # re-add dummy contents, if necessary
        if len(contents) == 0:
            contents += sciexp2.common.instance.Instance()

        self._contents = contents

    def _find_files(self, select, expression, *filters):
        return self._find_files_generic(select, expression, filters, set(),
                                        "finding files...")

    @_supports_view(_find_files)
    def find_files(self, expression, *filters):
        """Find paths matching a regular expression and add to `contents`.

        Parameters
        ----------
        expression : expression
            An expression for selecting paths.
        filters : list of filters, optional
            Filters that paths must match to be considered. All provided
            filters are AND'ed.

        Notes
        -----
        For each path matching `expression` and `filters`, extract it into an
        `~sciexp2.common.instance.Instance` and add to `contents`.

        The expression can contain arbitrarily complex `regular expressions
        <http://docs.python.org/library/re.html#regular-expression-syntax>`_,
        and variables are extracted from:

            - variable references: ``@varname@``
            - named re groups: ``(?P<varname>regexp)``

        You can use named re groups to limit which text matches into a variable,
        since the simpler ``@varname@`` form is equivalent to
        ``(?P<varname>[^@]+)``.

        Implicitly added variables:
            ======== ======================
            Name     Contents
            ======== ======================
            ``FILE`` the complete path name
            ======== ======================

        See also
        --------
        find_SPEC, find_simpoint

        """
        return self._find_files(None, expression, *filters)

    _find_SPEC__VARS = set(["SET", "BENCHMARK", "TEST", "DIR", "BINARY",
                            "STDIN", "PARAMS"])

    def _find_SPEC(self, select, base_dir, *filters):
        expression = os.path.join(base_dir, "benchspec",
                                  "@SET@", "@BENCHMARK@",
                                  "run", "(?:run_base_|000).*",
                                  "speccmds.cmd$")
        if not os.path.isabs(expression):
            expression = "./" + expression

        def process(instance):
            with open(utils.get_path(instance["FILE"])) as f:
                lines = f.readlines()

                # support both SPECcpu2006 and SPECcpu2000 style (respectively)
                assert lines[0].startswith("-C ") or lines[0].startswith("-u")

                dir_path = lines[0].split()[1]

                test = 0
                for line in lines[1:]:
                    new_instance = sciexp2.common.instance.Instance(instance)

                    elems = line.split()
                    if elems[0] == "-i":      # stdin
                        new_instance["STDIN"] = elems[1]
                        elems = elems[2:]
                    if elems[0] == "-o":      # stdout
                        elems = elems[2:]
                    if elems[0] == "-e":      # stderr
                        elems = elems[2:]
                    new_instance["DIR"] = dir_path
                    new_instance["BINARY"] = os.path.basename(elems[0])
                    new_instance["TEST"] = test
                    new_instance["PARAMS"] = " ".join(elems[1:])
                    new_instance["FILE"] = dir_path + os.sep +\
                                           new_instance["BINARY"]

                    test += 1
                    yield new_instance

        return self._find_files_generic(select, expression, filters,
                                        self._find_SPEC__VARS,
                                        "finding SPEC benchmarks...",
                                        process)

    @_supports_view(_find_SPEC)
    def find_SPEC(self, base_dir, *filters):
        """Find SPEC benchmarks and extract parameters.

        First searches the ``speccmds.cmd`` files for each benchmark with
        ``base_dir +
        "/benchspec/@SET@/@BENCHMARK@/run/(?:run_base_|000).*/speccmds.cmd"``,
        and then parses the ``speccmds.cmd`` files in order to generate one
        instance for each benchmark execution test.

        Parameters
        -----------
        base_dir : expression
            SPEC's base directory
        filters : list of filters, optional
            Filters that paths must match to be considered. All provided
            filters are AND'ed.

        Notes
        -----
        Implicitly added variables:
            ============= ======================
            Name          Contents
            ============= ======================
            ``SET``       set (e.g., CINT2000, CFP2000, CPU2006)
            ``BENCHMARK`` name (e.g., 400.perlbench)
            ``TEST``      test number
            ``DIR``       absolute path to prepared run directory
            ``BINARY``    executable file name
            ``STDIN``     standrad input file name
            ``PARAMS``    command line parameters
            ``FILE``      absolute path to executable
            ============= ======================

        See also
        --------
        find_files

        References
        ----------
        .. [1] http://www.spec.org

        """
        return self._find_SPEC(None, base_dir, *filters)

    def _find_simpoint(self, select, simpoints_expr, weights_expr, ignore):
        contents = self._contents

        # take care of dummy contents
        if len(contents) is 1 and len(list(contents.variables())) is 0:
            contents = sciexp2.common.instance.InstanceGroup()

        if select is None:
            select = sciexp2.common.filter.Filter()

        new_contents = sciexp2.common.instance.InstanceGroup()

        with progress.progressable_simple(
                contents, None, msg="finding simpoints...") as pcontents:
            for instance in pcontents:
                if not select.match(instance):
                    continue

                simpoints = _DICTXLATOR.xlate_rec(simpoints_expr, instance)
                simpoints = utils.get_path(simpoints)
                if not os.path.isfile(simpoints):
                    if not ignore:
                        raise ValueError("Could not find simpoints file: " +
                                         simpoints)
                    continue
                weights = _DICTXLATOR.xlate_rec(weights_expr, instance)
                weights = utils.get_path(weights)
                if not os.path.isfile(weights):
                    if not ignore:
                        raise ValueError("Could not find "
                                         "simpoint weights file: " + weights)
                    continue

                simpoints_list = []
                for line in open(simpoints):
                    (sp, idx) = line.split()
                    simpoints_list.insert(int(idx), sp)

                weights_list = []
                for line in open(weights):
                    (wg, idx) = line.split()
                    weights_list.insert(int(idx), wg)

                assert len(simpoints_list) == len(weights_list)
                for idx in range(0, len(simpoints_list)):
                    new_instance = sciexp2.common.instance.Instance(instance)
                    new_instance["SIMPOINT_ID"] = idx
                    new_instance["SIMPOINT_SP"] = simpoints_list[idx]
                    new_instance["SIMPOINT_WG"] = weights_list[idx]

                    new_contents.add(new_instance)

        # re-add dummy contents, if necessary
        if len(new_contents) == 0:
            new_contents += sciexp2.common.instance.Instance()

        self._contents = new_contents

    @_supports_view(_find_simpoint)
    def find_simpoint(self, simpoints_expr, weights_expr, ignore=False):
        """Expand current contents with SimPoint information.

        Expands the given arguments with current `contents` to find the
        results of `SimPoint` executions. This is useful to generate launchers
        for simulating what `SimPoint` found as representative.

        Parameters
        ----------
        simpoints_expr, weights_expr : expression
            Expression SimPoint's ``simpoints`` and ``weights`` output files.
        ignore : bool, optional
            Whether to ignore current `contents` that have no simpoint
            information available; otherwise aborts execution.

        Notes
        -----
        Implicitly added variables:
            =============== ======================
            Name            Contents
            =============== ======================
            ``SIMPOINT_ID`` simpoint index
            ``SIMPOINT_SP`` simpoint (e.g., basic block number)
            ``SIMPOINT_WG`` simpoint weight
            =============== ======================

        See also
        --------
        find_files

        References
        ----------
        .. [1] http://cseweb.ucsd.edu/~calder/simpoint

        """
        return self._find_simpoint(None, simpoints_expr, weights_expr, ignore)

    def _params(self, select, *filters, **params):
        append = params.pop("append", False)
        assert isinstance(append, bool)

        self._contents, self._deferred = _do_params(select, self._contents,
                                                    self._deferred, filters,
                                                    params, append)

    @_supports_view(_params)
    def params(self, *filters, **params):
        """Expand current `contents` with all valid parameter permutations.

        Substitutes the current `contents` with the `cartesian product` of
        current `contents` and all given parameter permutations.

        Parameters
        ----------
        filters : list of filters, optional
            Discard results not matching the given filters (default is to
            accept all).
        params : dict
            A dictionary of variable name / values pairs to perform
            permutations.

        Notes
        -----
        Values in `params` can have two forms:

         - A single value::

            params(a = 1)

         - An iterable container (e.g., a list to permute with all other
           variables, including the parameters)::

            params(a = [ 1, 10 ])

        Any of these forms can contain any of the following types (which can be
        mixed):

         - An immediate::

            params(var1 = [ 1, "valueN", math.log(1024, 2), ... ])

         - An :term:`expression` that will be :term:`expanded <expansion>`::

            params(var1 = [ "@other_param@-@another_one@", ...])

         - Deferred values:

           See `defer` for deferring the evaluation of still undefined
           variables.

        Providing a variable in `params` that already exists in `contents` will
        override its value. Note that the new value can reference any other
        variable in `contents`. Also, if the new value references variables not
        present in `contents`, values from `params` will be used instead.

        If variable `append` is present and set to `True`, the parameters will
        be appended to the contents, instead of being recombined with current
        contents.

        Examples
        --------
        >>> l = Launchgen()
        >>> l.params("a % 2 == 0",
        ...          a = range(4),
        ...          b = [ "foo", "bar" ])
        >>> l
        Launchgen([Instance({'a': 0, 'b': 'foo'}),
                   Instance({'a': 0, 'b': 'bar'}),
                   Instance({'a': 2, 'b': 'foo'}),
                   Instance({'a': 2, 'b': 'bar'})],
                  out='./out')

        New values reference old values (when available):

        >>> l.params(b = "@b@ (bis)",
        ...          c = "@b@-@a@")
        >>> l
        Launchgen([Instance({'a': 0, 'b': 'foo (bis)', 'c': 'foo-0'}),
                   Instance({'a': 0, 'b': 'bar (bis)', 'c': 'bar-0'}),
                   Instance({'a': 2, 'b': 'foo (bis)', 'c': 'foo-2'}),
                   Instance({'a': 2, 'b': 'bar (bis)', 'c': 'bar-2'})],
                  out='./out')

        New parameter combinations can also be appended, instead of combined
        with the existing ones:

        >>> with l.select("a == 0") as s:
        ...     s.params(append = True, x=[100, 200])
        >>> l
        Launchgen([Instance({'a': 0, 'b': 'foo (bis)', 'c': 'foo-0'}),
                   Instance({'a': 0, 'b': 'bar (bis)', 'c': 'bar-0'}),
                   Instance({'x': 100}),
                   Instance({'x': 200}),
                   Instance({'a': 2, 'b': 'foo (bis)', 'c': 'foo-2'}),
                   Instance({'a': 2, 'b': 'bar (bis)', 'c': 'bar-2'})],
                  out='./out')

        See also
        --------
        defer, sciexp2.common.filter.PFilter

        """
        return self._params(None, *filters, **params)

    def _pack(self, select, from_expr, to_expr, dereference=None):
        if dereference is None:
            dereference = self.dereference
        done = {}
        done_instances = {}
        expansions = _EXPANDER.expand(from_expr, self._contents,
                                      filter_=select,
                                      recursive=True)

        with progress.get(self._contents, msg="copying files...") as progr:
            for exp in six.itervalues(expansions):
                for instance in exp.instances:
                    progr()

                    exp_from = utils.get_path(exp.text)
                    exp_to = _DICTXLATOR.xlate_rec(to_expr, instance)
                    exp_to = utils.get_path(exp_to)

                    idx = exp_from + "+" + exp_to
                    if idx in done:
                        if not done[idx]:
                            done[idx] = True
                            progress.info(
                                "Skipping already packed file: %s -> %s",
                                exp_from, exp_to)
                            progress.verbose(
                                "Conflicting instances:\n%s\n%s",
                                done_instances[idx], instance)
                        continue
                    done[idx] = False
                    done_instances[idx] = instance

                    progress.debug("Packing: %s -> %s", exp_from, exp_to)

                    exp_to = self.out + os.sep + exp_to
                    utils.copy_path(exp_from, exp_to)

    @_supports_view(_pack)
    def pack(self, from_expr, to_expr, dereference=None):
        """Copy files from source to destination.

        Parameters
        ----------
        from_expr, to_expr : expression
            Source/destination file expressions.
        dereference : bool, optional
            Whether to dereference symlinks in source files (defaults to
            ``self.dereference``).

        Notes
        -----
        Multiple source expressions could have a single destination, in which
        case this is noted with the message ``Skipping already packed file:
        <source> -> <destination>``.

        The copy is performed only if the source is newer than the destination,
        or if the destination does not exist.

        """
        return self._pack(None, from_expr, to_expr, dereference)

    def _translate(self, select, expression, instance=None):
        if instance:
            return _DICTXLATOR.xlate_rec(expression, instance)
        elif select is None:
            return [_DICTXLATOR.xlate_rec(expression, i)
                    for i in self.contents]
        else:
            return [_DICTXLATOR.xlate_rec(expression, i)
                    for i in self.contents
                    if select.match(i)]

    @_supports_view(_translate)
    def translate(self, expression, instance=None):
        """Return list of translations for given expression.

        Parameters
        ----------
        instance : instance, optional
            Only translate given expression (returns a string).

        See also
        --------
        expand

        Examples
        --------
        >>> l = Launchgen()
        >>> l.params("a % 2 == 0",
        ...          a = range(4),
        ...          b = [ "foo", "bar" ])
        >>> l
        Launchgen([Instance({'a': 0, 'b': 'foo'}),
                   Instance({'a': 0, 'b': 'bar'}),
                   Instance({'a': 2, 'b': 'foo'}),
                   Instance({'a': 2, 'b': 'bar'})],
                  out='./out')

        >>> l.translate("@a@")
        ['0', '0', '2', '2']
        >>> l.translate("@a@-@b@", list(l.contents)[1])
        '0-bar'
        >>> l.translate("@a@-@b@", {'a': 3, 'b': 'baz'})
        '3-baz'

        """
        return self._translate(None, expression, instance)

    def _expand(self, select, expression, **kwargs):
        with_view = kwargs.pop("with_view", False)
        utils.assert_kwargs(kwargs)

        if select is None:
            filter_ = None
        else:
            filter_ = sciexp2.common.filter.Filter(select)

        expansions = _EXPANDER.expand(expression, self._contents,
                                      filter_=filter_,
                                      recursive=True,
                                      with_filter=with_view)
        if not with_view:
            expansions = list(expansions.keys())
        else:
            if filter_ is None:
                filter_ = sciexp2.common.filter.Filter()
            expansions = [(res.text, self.select(filter_ & res.filter))
                          for res in expansions.values()]
        return expansions

    @_supports_view(_expand)
    def expand(self, expression, **kwargs):
        """Return a list with the expansions of the given expression.

        Parameters
        ----------
        expression
            Expression to expand.
        with_view : bool, optional
            Return a list of expansion and `LaunchgenView` pairs (default is
            `False`).

        See also
        --------
        translate

        Examples
        --------
        >>> l = Launchgen()
        >>> l.params("a % 2 == 0",
        ...          a = range(4),
        ...          b = [ "foo", "bar" ])
        >>> l
        Launchgen([Instance({'a': 0, 'b': 'foo'}),
                   Instance({'a': 0, 'b': 'bar'}),
                   Instance({'a': 2, 'b': 'foo'}),
                   Instance({'a': 2, 'b': 'bar'})],
                  out='./out')

        >>> l.expand("@a@")
        ['0', '2']
        >>> l.expand("@a@", with_view=True)     #doctest: +NORMALIZE_WHITESPACE
        [('0', Launchgen([Instance({'a': 0, 'b': 'foo'}),
                          Instance({'a': 0, 'b': 'bar'})],
                         out='./out')),
         ('2', Launchgen([Instance({'a': 2, 'b': 'foo'}),
                          Instance({'a': 2, 'b': 'bar'})],
                         out='./out'))]
        >>> l.select("b == 'foo'").expand("@a@", with_view=True) #doctest: +NORMALIZE_WHITESPACE
        [('0', Launchgen([Instance({'a': 0, 'b': 'foo'})],
                         out='./out')),
         ('2', Launchgen([Instance({'a': 2, 'b': 'foo'})],
                         out='./out'))]

        """
        return self._expand(None, expression, **kwargs)

    def _generate_generic(self, select, from_expr, to_expr,
                          default_values, pre_values, filters, values,
                          post_generate):
        """Generate files using current contents and given values.

        Evaluates any deferred value before file generation.

        See also
        --------
        _do_generate

        """
        # defaults might be overriden only on some of the instances
        # separate those that the user has not specified from the rest
        default_values_maybe = dict(
            [(var, val)
             for var, val in six.iteritems(default_values)
             if var in self._contents or var in values])
        default_values = dict(
            [(var, val)
             for var, val in six.iteritems(default_values)
             if var not in default_values_maybe])

        # merge (non-defined) default_values into values
        values = dict(values)
        values.update(default_values)

        # merge contents and values
        contents, deferred = _do_params(select, self._contents, self._deferred,
                                        filters, values, False)

        # late evaluation of deferred values
        if len(deferred) is not 0:
            contents.cache_reset()
            for instance in deferred:
                for key in six.iterkeys(instance):
                    if not defer_evaluate(instance, key):
                        raise ValueError("Deferral of '%s' cannot "
                                         "be evaluated" % key)

        if select is not None:
            contents = sciexp2.common.instance.InstanceGroup(
                contents.select(select))

        if len(contents) == 0:
            return sciexp2.common.instance.InstanceGroup()
        else:
            return _do_generate(contents, from_expr, to_expr, self.out,
                                default_values, pre_values,
                                post_generate)

    def _generate(self, select, from_expr, to_expr, *filters, **values):
        def post_generate(path, instance, xlator):
            pass
        self._generate_generic(select, from_expr, to_expr,
                               {}, {}, filters, values,
                               post_generate)

    @_supports_view(_generate)
    def generate(self, from_expr, to_expr, *filters, **values):

        """Generate files by string translation.

        Much like `pack`, generates files from source templates, by way of
        translating all variable references into its values.

        For each expansion of `from_expr` with the current contents, uses the
        resulting instances to expand `to_expr`. Then uses `values` and the
        instance resulting of the `to_expr` expansion to translate the contents
        of the source.

        Parameters
        ----------
        from_expr, to_expr : expression
            Source/destination file expressions.
        filters : list of filters, optional
            Discard results not matching the given filters (default is to
            accept all).
        values : dict
            Additional variables to translate in destination files.

        Notes
        -----
        Arguments `filters` and `values` are interpreted as in `params` to
        (optionally) create some temporary contents that are then used to
        perform the actual file generation.

        If a single expansion of `to_expr` produces more than one matching
        instance, only the first one is used and noted with the message
        ``Skipping already generated file: <source> -> <destination>``.

        If it already exists, the destination file is only modified if its new
        contents are different from its current ones.

        See also
        --------
        params

        """
        return self._generate(None, from_expr, to_expr, *filters, **values)

    def _launcher(self, select, template, to_expr, *export, **values):
        tpl = templates.get(template)
        tpl_system = tpl.system

        jd = utils.get_path(values.pop("JD", "jobs.jd"))
        if not os.path.isabs(jd):
            jd = self.out + os.sep + jd
        out_abs = os.path.abspath(utils.get_path(self.out))
        jd = os.path.relpath(jd)
        jd_abs = os.path.abspath(jd)
        if jd_abs[:len(out_abs)] != out_abs:
            raise ValueError("Job descriptor file must be inside "
                             "the output directory")
        jd_base = os.path.dirname(jd_abs[len(out_abs)+1:])

        for reserved in set.union(tpl_system.defines(), ["LAUNCHER"]):
            if reserved in values or reserved in self._contents:
                raise ValueError("'%s' is a reserved variable" % reserved)

        values["LAUNCHER"] = to_expr

        if len(export) > 0:
            warnings.warn("Use of deprecated argument 'export' in method "
                          "'Launchgen.launcher'")
            exports = set(export)
        exports = set(values.pop("EXPORTS", []))

        depends = values.pop("DEPENDS", [])
        if isinstance(depends, six.string_types):
            raise TypeError("DEPENDS must be a sequence of strings")
        depends = set(str(d) for d in depends)
        depends.add("LAUNCHER")
        depends_unknown = [dep for dep in depends
                           if dep not in self._contents and dep not in values]
        if len(depends_unknown):
            raise ValueError("Unknown dependencies: %s" %
                             ",".join(depends_unknown))

        # TODO: should export used variables
        submit_args = values.pop("SUBMIT_ARGS", [])
        if isinstance(submit_args, six.string_types) or \
           not isinstance(submit_args, collections.Iterable):
            raise TypeError("Argument 'SUBMIT_ARGS' is not a list of strings")
        submit_args = tpl.submit_args + submit_args
        submit_args = [str(i) for i in submit_args]

        def post_generate(path, instance, xlator):
            tpl_system.post_generate(self.out, path, instance, xlator)
        group = self._generate_generic(select, tpl.template_path,
                                       to_expr,
                                       tpl.defaults, tpl.overrides,
                                       [], values,
                                       post_generate)

        if len(group) == 0:
            launcher.save(jd, jd_base, tpl.system, group, set(), depends,
                          submit_args)
        else:
            # select variables to export
            exports = set(tpl_system.assumes()) | depends | exports
            if len(exports - set(group.variables())) > 0:
                raise ValueError("Unknown variables to export: " +
                                 ", ".join(exports - set(group.variables())))

            # generate job descriptor file
            launcher.save(jd, jd_base, tpl.system, group, exports, depends,
                          submit_args)

    @_supports_view(_launcher)
    def launcher(self, template, to_expr, *export, **values):
        """Generate files from predefined templates.

        Performs the same work as `generate` with a predefined source file
        (identified by `template`) and additionally creates a job descriptor
        file in the output directory, which can be later used by `launcher`.

        The job descriptor will contain all variables used in `to_expr` (to
        identify the jobs by the parameters used to generate their files) and
        those listed in `export` (to provide further identification variables
        established by the user).

        Parameters
        ----------
        template : str
            Source template name
        to_expr : expression
            Destination job launcher file expression.
        export : list of str, optional
            Deprecated in favour of *EXPORTS* in argument `values`.
        values : dict
            Additional variables to translate in destination files.

        See also
        --------
        generate
        sciexp2.templates : Retrieve and manage launcher templates.

        Notes
        -----
        Variables *DONE* and *FAIL* are used as file paths by `launcher` to
        identify that a job has been run, and whether it has failed
        (respectively).

        If a variable in the current contents is also present in `values`, the
        one in `values` will overwrite the contents.

        The following variables are implicitly set:

        ========== =======================
        Name       Description
        ========== =======================
        *LAUNCHER* Expansion of `to_expr`.
        ========== =======================

        The following variables have a special meaning in argument `values`:

        ============= ============= ==========================================
        Name          Default value Description
        ============= ============= ==========================================
        *JD*          ``"jobs.jd"`` Job descriptor file to use with
                                    `launcher`. Not expanded.
        *EXPORTS*     []            Variable names to export.
        *DEPENDS*     ["LAUNCHER"]  Extra job dependencies. Not expanded.
                                    Automatically exported.
        *SUBMIT_ARGS* []            Extra arguments to job-submitting program.
        ============= ============= ==========================================

        *EXPORTS* is a list of variable names whose values will be exported to
        the job descriptor file. By exporting them, you can later use these
        variables as filters on *launcher* commands.

        *DEPENDS* is a list of variable names whose values point to files. If
        any of those files does not exist or is newer than *DONE*, the job will
        be considered for reexecution. Variable *LAUNCHER* is always implicitly
        added into the list. If the variable value for an instance contains the
        empty string, it is ignored as a dependency.

        You must export all variables (directly or indirectly) used in
        *SUBMIT_ARGS*.

        """
        return self._launcher(None, template, to_expr, *export, **values)


######################################################################
# Parameter recombination

def _get_product(contents_vars, params):
    """Compute what the given `params` are defining."""
    if len(params) > 0:
        var, vals = params[0]
        params = params[1:]
        for val in vals:
            for rest in _get_product(contents_vars, params):
                res = {var: val}
                res.update(rest[0])

                xlate = rest[1]
                deferred = rest[2]
                if isinstance(val, six.string_types) and \
                   len(set(varref.expr_get_vars("@", val)) & contents_vars) > 0:
                    xlate.add(var)
                elif isinstance(val, _DeferAtom) and\
                     len(val.deferred() & contents_vars) > 0:
                    deferred.add(var)

                yield (res, xlate, deferred)
    else:
        yield (dict(), set(), set())


def _do_recombine(base_instance,
                  product, product_in_xlate, product_in_deferred,
                  product_xlate, product_deferred,
                  new_deferred, new_deferred_vars):
    """Generate new instances using the given parameter products."""
    new_deferred.discard(base_instance)

    for prod in product:
        res = sciexp2.common.instance.Instance(base_instance)

        # resolve old value references on new values
        for var, val in six.iteritems(prod):
            if var in product_in_xlate:
                val = _DICTXLATOR.xlate_rec(val, base_instance,
                                            allow_unxlated=True)
            elif var in product_in_deferred:
                # TODO: if evaluation fails partially, it will only be
                #       reevaluated later on, when the original value is no
                #       longer available
                val = val.defer_evaluate(res)

            res[var] = val

        # resolve new references ASAP
        for var in product_xlate:
            res[var] = _DICTXLATOR.xlate_rec(res[var], res,
                                             allow_unxlated=True)
        still_deferred = False
        for var in product_deferred:
            if not defer_evaluate(res, var):
                still_deferred = True
                new_deferred_vars.add(var)
        if still_deferred:
            new_deferred.add(res)

        yield res


def _do_params(select, contents, deferred, filters, params, append):
    new_vars = set(contents.variables()) | set(six.iterkeys(params))
    filters = sciexp2.common.filter.Filter(*filters)
    filters.validate(new_vars)

    if len(params) == 0:
        return contents, deferred

    # normalize `params`
    for var, val in six.iteritems(params):
        if not isinstance(val, collections.Iterable) or \
           isinstance(val, six.string_types):
            val = [val]
        if not isinstance(val, collections.Sized):
            val = list(val)
        params[var] = val

    params_xlate = set([var for var, vals in six.iteritems(params)
                        if any(isinstance(val, six.string_types) and
                               len(set(varref.expr_get_vars("@", val))) > 0
                               for val in vals)])
    params_deferred = set([var for var, vals in six.iteritems(params)
                           if any(isinstance(val, _DeferAtom)
                                  for val in vals)])
    params_size = functools.reduce(operator.mul,
                                   (len(val) for val in six.itervalues(params)),
                                   1)

    def empty_contents(contents):
        return len(contents) == 0 or \
            (len(contents) == 1 and
             contents.get_index(0) == sciexp2.common.instance.Instance())

    if append:
        if empty_contents(contents):
            contents = sciexp2.common.instance.InstanceGroup()
        if select is None:
            new_size = params_size + params_size
            new_contents = contents
        else:
            new_size = len(contents) + params_size + params_size
            new_contents = sciexp2.common.instance.InstanceGroup()
    else:
        new_size = len(contents) * params_size + params_size
        new_contents = sciexp2.common.instance.InstanceGroup()
    new_deferred = set(deferred)

    with progress.get(new_size, msg="calculating parameters...") as progr:
        product = []
        product_in_xlate = set()
        product_in_deferred = set()

        # ensure `params` order across runs
        params_sorted = sorted(six.iteritems(params),
                               key=lambda i: i[0])

        for instance, xlate, deferred in _get_product(
                set(contents.variables()), params_sorted):
            product.append(instance)
            product_in_xlate |= xlate
            product_in_deferred |= deferred
            progr()

        def add_recombinations(instance):
            new_deferred_vars = set()
            for new_instance in _do_recombine(
                    instance, product,
                    product_in_xlate, product_in_deferred,
                    params_xlate, params_deferred,
                    new_deferred, new_deferred_vars):
                if len(new_deferred_vars) > 0:
                    filters.validate(new_vars - new_deferred_vars)
                if filters.match(new_instance):
                    new_contents.add(new_instance)
                progr()

        if append:
            if select is None:
                add_recombinations(sciexp2.common.instance.Instance())
            else:
                selected = False
                for instance in contents:
                    if select.match(instance):
                        selected = True
                        new_contents.add(instance)
                        progr()
                    else:
                        if selected:
                            selected = False
                            add_recombinations(
                                sciexp2.common.instance.Instance())
                        new_contents.add(instance)
                        progr()

        else:                           # not append
            if select is None:
                for instance in contents:
                    add_recombinations(instance)
            else:
                for instance in contents:
                    if not select.match(instance):
                        new_contents.add(instance)
                        progr(params_size)
                    else:
                        add_recombinations(instance)

    if empty_contents(new_contents):
        new_contents += sciexp2.common.instance.Instance()

    return new_contents, new_deferred


######################################################################
# File generation

def _do_generate(instances, from_expr, to_expr, to_dir,
                 default_values, pre_values,
                 post_generate):
    """Generate files using given contents and values.

    Parameters
    ----------
    instances : InstanceGroup
        Group to perform expansions and value substitutions.
    from_expr, to_expr : expression
        Source/destination file expressions.
    to_dir : str
        Destination directory (appended into `to_expr`).
    default_values : dict
        Substitutions to perform on certain instances if not present.
    pre_values : dict
        Initial substitutions to perform.
    post_generate : function
        Function to call after generating a file. Function receives the
        instance used to generate the file, and a path to the generated file.

    Returns
    -------
    InstanceGroup
        Group with an instance with fully expanded values for each
        destination file.

    See also
    --------
    _do_generate_from

    """
    res = sciexp2.common.instance.InstanceGroup()

    with progress.get(instances, msg="generating files...") as progr:
        # expand on source file
        if len(varref.expr_get_vars("@", from_expr, True)) == 0:
            # shortcut for a single source file (hopefully the usual path)
            for instance in _do_generate_from(
                    instances, from_expr,
                    to_expr, to_dir,
                    default_values, pre_values,
                    post_generate,
                    progr):
                res.add(instance)
        else:
            # not the optimal solution as a full expansion on 'from_expr' will
            # eat many unnecessary cicles, because the result will have to be
            # expanded again with 'to_expr'
            from_expansions = _EXPANDER.expand(from_expr, instances,
                                               grouped=True, recursive=True)
            for from_expand in six.itervalues(from_expansions):
                from_path = utils.get_path(from_expand.text)
                for instance in _do_generate_from(
                        from_expand.instances, from_path,
                        to_expr, to_dir,
                        default_values, pre_values,
                        post_generate,
                        progr):
                    res.add(instance)

    return res


def _do_generate_from(instances, from_path, to_expr, to_dir,
                      default_values, pre_values,
                      post_generate,
                      progr):
    """Generate files using given contents and values.

    Parameters
    ----------
    instances : InstanceGroup
        Group to perform expansions and value substitutions.
    from_path : str
        Source file path.
    to_expr : expression
        Destination file expression.
    to_dir : str
        Destination directory (appended into `to_expr`).
    default_values : dict
        Substitutions to perform on certain instances if not present.
    pre_values : dict
        Initial substitutions to perform.
    post_generate : function
        Function to call after generating a file. Function receives the
        instance used to generate the file, a path to the generated file, and
        the xlator used to generate the file.
    progr
        Progress reporter.

    Returns
    -------
    Instance generator
        Instances with fully expanded values for each destination file.

    See also
    --------
    _do_generate_file

    """
    with open(from_path) as from_file:
        from_contents = from_file.readlines()

    # apply pre_values and default_values once and for all
    new_from_contents = []
    for line in from_contents:
        line = _DICTXLATOR.xlate(line, pre_values, allow_unxlated=True)
        line = _DICTXLATOR.xlate_rec(line, default_values, allow_unxlated=True)
        new_from_contents.append(line)
    from_contents = new_from_contents

    # expand on destination file
    to_expansions = _EXPANDER.expand(to_expr, instances, recursive=True)
    for to_expand in six.itervalues(to_expansions):
        if len(to_expand.instances) > 1:
            progress.info(
                "Skipping already generated file: %s -> %s",
                from_path, to_expand.text)
            progress.verbose(
                "Conflicting instances:\n%s\n%s",
                 to_expand.instances.get_index(0),
                 to_expand.instances.get_index(1))

        to_path = utils.get_path(to_expand.text)
        if not os.path.isabs(to_path):
            to_path = os.path.join(to_dir, to_path)

        if not os.path.exists(to_path):
            with utils.get_file(to_path, "w") as to_file:
                progress.debug("Generating: %s -> %s", from_path, to_path)
                res = _do_generate_file(to_expand.instances.get_index(0),
                                        from_contents, to_file, default_values)
                shutil.copymode(from_path, to_path)
                post_generate(to_path, res, _DICTXLATOR)
        else:
            with utils.get_tmp_file() as to_file:
                res = _do_generate_file(to_expand.instances.get_index(0),
                                        from_contents, to_file, default_values)
                to_file.flush()
                if utils.copy_path_maybe(to_file.name, to_path):
                    progress.debug("Generating: %s -> %s", from_path, to_path)
                    shutil.copymode(from_path, to_path)
                    post_generate(to_path, res, _DICTXLATOR)

        progr(len(to_expand.instances))
        yield res


def _do_generate_file(instance, from_contents, to_file, default_values):
    """Generate a file using given contents and values.

    Parameters
    ----------
    instance : Instance
        Instance to perform implicit translation with.
    from_contents : list(str)
        Untranslated source contents.
    to_file : file
        Destination file.
    default_values : dict
        Substitutions to perform on certain instances if not present.

    Returns
    -------
    Instance
        Instance with fully expanded values.

    """
    res = sciexp2.common.instance.Instance(instance)
    # make sure all values are fully expanded
    for var, val in six.iteritems(res):
        res[var] = _DICTXLATOR.xlate_rec(val, res)

    # if necessary, add defaults
    default_values_real = []
    for key, val in six.iteritems(default_values):
        if key not in res:
            res[key] = val
            default_values_real.append(key)
    # ensure added defaults are final
    # TODO: only necessary if the variable is going to be exported
    for key in default_values_real:
        res[key] = _DICTXLATOR.xlate_rec(res[key], res)

    # actually write file contents
    # (line-by-line to provide more readable errors)
    for line in from_contents:
        line = _DICTXLATOR.xlate(line, res)
        to_file.write(line)

    return res


######################################################################
# Views

class LaunchgenView (pp.Pretty):
    """Proxy to a subset of elements in a `Launchgen` instance.

    Notes
    -----
    Views follow the context manager protocol, which can be used to improve
    code readability:

    >>> l = Launchgen()
    >>> l.params(a=range(2), b=range(2))
    >>> with l.select("a != b") as v, v.select_inverse() as i:
    ...     v.params(c=1)
    ...     i.params(c=2)
    >>> l
    Launchgen([Instance({'a': 0, 'b': 0, 'c': 2}),
               Instance({'a': 0, 'b': 1, 'c': 1}),
               Instance({'a': 1, 'b': 0, 'c': 1}),
               Instance({'a': 1, 'b': 1, 'c': 2})],
              out='./out')

    """

    def __init__(self, launchgen, filter_base, filter_top,
                 **kwargs):
        assert len(kwargs) == 0
        self._launchgen = launchgen
        self._filters = [filter_base, filter_top]
        for filter_ in self._filters:
            filter_.validate(set(self._launchgen.contents.variables()))

    def _repr_pretty_(self, p, cycle):
        self._launchgen._do_repr_pretty_(self._as_filter(), p, cycle)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def _as_filter(self):
        return sciexp2.common.filter.Filter(*self._filters)

    @property
    def contents(self):
        res = self._launchgen._contents.select(self._as_filter())
        return sciexp2.common.instance.InstanceGroup(res)

    def select(self, *filters):
        """Select a subset of this view.

        See also
        --------
        Launchgen.select

        """
        return LaunchgenView(self._launchgen,
                             self._as_filter(),
                             sciexp2.common.filter.Filter(*filters))

    def select_inverse(self):
        """Get the inverse selection of this view.

        If using nested views, this will invert the filter of this one, not all
        filters for parent views.

        See also
        --------
        Launchgen.select

        """
        return self._launchgen.select(
            sciexp2.common.filter.Filter(self._filters[0],
                                         "!(%s)" % self._filters[1]))

    def __getattr__(self, name):
        if name in ["_launchgen", "_filters"]:
            object.__getattribute__(self, name)
        else:
            attr = getattr(self._launchgen, name)
            if callable(attr):
                if attr.__name__ in VIEW_SUPPORTED:
                    attr = getattr(self._launchgen,
                                   VIEW_SUPPORTED[attr.__name__])

                def func(*args, **kwargs):
                    return attr(self._as_filter(), *args, **kwargs)
                return func
            else:
                return attr

    def __setattr__(self, name, value):
        if name in ["_launchgen", "_filters"]:
            object.__setattr__(self, name, value)
        else:
            attr = getattr(self._launchgen, name)
            assert not callable(attr)
            setattr(self._launchgen, name, value)


######################################################################
# Deferred evaluation

class _DeferAtom:
    """A piece in a deferred chain of operations."""

    def _check_deferred(self, maydefer, update=True):
        res = set()
        for i in maydefer:
            if isinstance(i, _DeferAtom):
                res |= i.deferred()
        if update:
            self._defer = res
        return res

    def deferred(self):
        """Return a set with deferred IDs."""
        return self._defer

    def __str__(self):
        raise ValueError("Tried to implicitly evaluate the deferral of: " +
                         ", ".join(self.deferred()))

    # definitions for implicit lookups

    def __add__(self, arg):
        return _DeferCall(self, "__add__", arg)

    def __radd__(self, arg):
        return _DeferCall(self, "__radd__", arg)

    def __sub__(self, arg):
        return _DeferCall(self, "__sub__", arg)

    def __rsub__(self, arg):
        return _DeferCall(self, "__rsub__", arg)

    def __mul__(self, arg):
        return _DeferCall(self, "__mul__", arg)

    def __rmul__(self, arg):
        return _DeferCall(self, "__rmul__", arg)

    def __div__(self, arg):
        return _DeferCall(self, "__div__", arg)

    def __rdiv__(self, arg):
        return _DeferCall(self, "__rdiv__", arg)

    def __mod__(self, arg):
        return _DeferCall(self, "__mod__", arg)

    def __rmod__(self, arg):
        return _DeferCall(self, "__rmod__", arg)


class _DeferInstance (_DeferAtom):
    """Deferred access to instance variable."""

    def __init__(self, name):
        self._name = name
        self._defer = set([name])

    def defer_evaluate(self, current, level=0):
        if self._name not in current:
            return self
        res = current[self._name]
        if isinstance(res, _DeferAtom):
            res = res.defer_evaluate(current, level+1)
        return res


class _DeferCall (_DeferAtom):
    """Deferred procedure call."""

    def __init__(self, obj, func, *args, **kwargs):
        assert isinstance(func, str) or callable(func)
        self._obj = obj
        self._func = func
        self._args = args
        self._kwargs = kwargs
        defer = list(self._args) + list(self._kwargs.values()) + [self._obj]
        self._check_deferred(defer)

    def defer_evaluate(self, current, level=0):
        # evaluate function arguments
        args = []
        for arg in self._args:
            if isinstance(arg, _DeferAtom):
                arg = arg.defer_evaluate(current, level+1)
            args.append(arg)

        kwargs = {}
        for key, val in six.iteritems(self._kwargs):
            if isinstance(val, _DeferAtom):
                val = val.defer_evaluate(current, level+1)
            kwargs[key] = val

        if len(self._check_deferred(args + list(kwargs.values()),
                                    False)) is not 0:
            return self

        # evaluate function
        if self._obj is None:
            return self._func(*args, **kwargs)
        else:
            obj = self._obj
            if isinstance(obj, _DeferAtom):
                obj = obj.defer_evaluate(current, level+1)
            if isinstance(obj, _DeferAtom):
                return self
            return getattr(obj, self._func)(*args, **kwargs)


def defer(arg, *args, **kwargs):
    """Return a deferrable value.

    Automatically detect the type of deferral through the type of `arg`:

      - variable access::

              params(P2 = defer("P1") * 2)
              params(P1 = [ 1, 2, 3, 4 ])

        Due to limitations in Python, non-numeric operations cannot be applied
        on the result of a call to `defer` (e.g., comparisons and boolean
        operators like `and` and `or`). In this case, a function call should be
        used.

      - function call::

              params(P2 = defer(math.log, defer("P1"), 2))
              params(P1 = [ 1, 2, 3, 4 ])

    Deferred values can be infinitely nested, such that these are not evaluated
    until all deferred values are available.

    """
    if isinstance(arg, str):
        assert len(args) is 0 and len(kwargs) is 0
        return _DeferInstance(arg)
    else:
        assert callable(arg)
        return _DeferCall(None, arg, *args, **kwargs)


def defer_evaluate(instance, key):
    """Replace ``instance[key]`` with the result of its evaluation.

    Returns whether the given key could be evaluated.

    """
    val = instance[key]
    if isinstance(val, _DeferAtom):
        val = val.defer_evaluate(instance)
        if isinstance(val, _DeferAtom):
            return False
        instance[key] = val
    return True


__all__ = [
    "file_contents", "Launchgen", "LaunchgenView", "defer", "defer_evaluate",
]
