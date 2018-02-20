import os
import re
import sys

from coverage import cmdline


PYTHON_FILE = re.compile(r'(.*)\.py')


def get_module_names_under(path):
    for entry in os.listdir(path):
        if os.path.isdir(os.path.join(path, entry)):
            if os.path.exists(os.path.join(path, entry, '__init__.py')):
                yield entry
        else:
            match = PYTHON_FILE.fullmatch(entry)
            if match:
                yield entry.group(1)


def insert_unique(lst, item):
    if item not in lst:
        lst.append(item)


class CustomScript(cmdline.CoverageScript):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.module_coverage = {}
        self.coverage_args = {}
        self.current_coverage = None
        self.import_coverage = None
        self.options = None
        self.code_ran = None

    def make_import_coverage(self, roots):
        kwargs = self.coverage_args.copy()
        kwargs['source'] = sorted(set(kwargs['source']).union(roots))
        self.import_coverage = self.covpkg.Coverage(**kwargs)

    def new_coverage(self, test_path, module_paths):
        # This should only be called during "run"
        kwargs = self.coverage_args.copy()
        kwargs['source'] = kwargs['source'].copy()
        insert_unique(kwargs['source'], test_path)
        for path in module_paths:
            insert_unique(kwargs['source'], path)
        self.module_coverage[test_path] = self.covpkg.Coverage(**kwargs)

    def _end_coverage(self):
            self.current_coverage.stop()
            if self.code_ran:
                data_file = self.current_coverage.get_option("run:data_file")
                if self.path_exists(data_file):
                    self.current_coverage.combine(data_paths=[data_file])
            self.current_coverage.save()

    def switch_coverage(self, target_coverage):
        if self.current_coverage is not target_coverage:
            self._end_coverage()
            self.current_coverage = target_coverage
            self.current_coverage.start()

    def activate_coverage(self, test_path):
        target_coverage = self.module_coverage.get(test_path)
        if target_coverage:
            self.switch_coverage(target_coverage)
        else:
            print('Unknown test path: {}'.format(test_path))

    def deactivate_coverage(self):
        self.switch_coverage(self.coverage)

    def command_line(self, argv):
        """The bulk of the command line interface to coverage.py.

        `argv` is the argument list to process.

        Returns 0 if all is well, 1 if something went wrong.

        """
        # Collect the command-line options.
        if not argv:
            self.help_fn(topic='minimum_help')
            return cmdline.OK

        # The command syntax we parse depends on the first argument.  Global
        # switch syntax always starts with an option.
        self.global_option = argv[0].startswith('-')
        if self.global_option:
            parser = cmdline.GlobalOptionParser()
        else:
            parser = cmdline.CMDS.get(argv[0])
            if not parser:
                self.help_fn("Unknown command: '%s'" % argv[0])
                return cmdline.ERR
            argv = argv[1:]

        parser.help_fn = self.help_fn
        ok, options, args = parser.parse_args_ok(argv)
        if not ok:
            return cmdline.ERR

        # Handle help and version.
        if self.do_help(options, args, parser):
            return cmdline.OK

        # We need to be able to import from the current directory, because
        # plugins may try to, for example, to read Django settings.
        sys.path[0] = ''

        # Listify the list options.
        source = (cmdline.unshell_list(options.source) or []) + ['tests']
        omit = cmdline.unshell_list(options.omit)
        include = cmdline.unshell_list(options.include)
        debug = cmdline.unshell_list(options.debug)

        self.options = options

        self.coverage_args = dict(
            data_suffix=options.parallel_mode,
            cover_pylib=options.pylib,
            timid=options.timid,
            branch=options.branch,
            config_file=options.rcfile,
            source=source,
            omit=omit,
            include=include,
            debug=debug,
            concurrency=options.concurrency,
        )

        # Do something.
        self.current_coverage = self.coverage = self.covpkg.Coverage(
            **self.coverage_args)

        if options.action == "debug":
            return self.do_debug(args)

        elif options.action == "erase":
            self.coverage.erase()
            return cmdline.OK

        elif options.action == "run":
            return self.do_run(options, args)

        elif options.action == "combine":
            if options.append:
                self.coverage.load()
            data_dirs = args or None
            self.coverage.combine(data_dirs, strict=True)
            self.coverage.save()
            return cmdline.OK

        # Remaining actions are reporting, with some common options.
        report_args = dict(
            morfs=cmdline.unglob_args(args),
            ignore_errors=options.ignore_errors,
            omit=omit,
            include=include,
        )

        self.coverage.load()

        total = None
        if options.action == "report":
            total = self.coverage.report(
                show_missing=options.show_missing,
                skip_covered=options.skip_covered, **report_args)
        elif options.action == "annotate":
            self.coverage.annotate(
                directory=options.directory, **report_args)
        elif options.action == "html":
            total = self.coverage.html_report(
                directory=options.directory, title=options.title,
                skip_covered=options.skip_covered, **report_args)
        elif options.action == "xml":
            outfile = options.outfile
            total = self.coverage.xml_report(outfile=outfile, **report_args)

        if total is not None:
            # Apply the command line fail-under options, and then use the
            # config value, so we can get fail_under from the config file.
            if options.fail_under is not None:
                self.coverage.set_option("report:fail_under",
                                         options.fail_under)

            fail_under = self.coverage.get_option("report:fail_under")
            precision = self.coverage.get_option("report:precision")
            if cmdline.should_fail_under(total, fail_under, precision):
                return cmdline.FAIL_UNDER

        return cmdline.OK

    def do_run(self, options, args):
        """Implementation of 'coverage run'."""

        if not args:
            self.help_fn("Nothing to do.")
            return cmdline.ERR

        if options.append and self.coverage.get_option("run:parallel"):
            self.help_fn("Can't append to data files in parallel mode.")
            return cmdline.ERR

        if options.concurrency == "multiprocessing":
            # Can't set other run-affecting command line options with
            # multiprocessing.
            for opt_name in ['branch', 'include', 'omit', 'pylib', 'source',
                             'timid']:
                # As it happens, all of these options have no default, meaning
                # they will be None if they have not been specified.
                if getattr(options, opt_name) is not None:
                    self.help_fn(
                        "Options affecting multiprocessing must be specified "
                        "in a configuration file."
                    )
                    return cmdline.ERR

        if not self.coverage.get_option("run:parallel"):
            if not options.append:
                self.coverage.erase()

        self.coverage.start()
        if os.path.isdir('src'):
            roots = sorted(set(get_module_names_under('src')))
            self.make_import_coverage(roots)
            print('Covering packages under: {}'.format(roots))
            self.switch_coverage(self.import_coverage)
        self.code_ran = True
        try:
            if options.module:
                self.run_python_module(args[0], args)
            else:
                filename = args[0]
                self.run_python_file(filename, args)
        except cmdline.NoSource:
            self.code_ran = False
            raise
        finally:
            self._end_coverage()

        return cmdline.OK


coverage_script = CustomScript()
