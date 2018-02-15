"""Unit tests for the Runner Class"""
import glob
import json
import os
import random
import shutil
import stat
import string
import tempfile
import unittest

try:
    import StringIO as io
except ImportError:
    import io

import runsteps


def fill_directory(path, files):
    """Populate a directory with empty files
    Args:
        files: A dictionary where the keys are filenames and the value is
               a string of content to fill the file. None or False as values
               will create the file without content and without the executable
               bit.
    Returns: A list of the full paths of added files
    """
    paths = []
    for file, executable in files.items():
        fullpath = '/'.join([path, file])
        open(fullpath, 'w').close()
        if executable:
            with open(fullpath, 'w') as newfile:
                newfile.write(str(executable))
            filestat = os.stat(fullpath)
            os.chmod(fullpath, filestat.st_mode | stat.S_IXUSR)
        paths.append(fullpath)
    return paths


class RunnerTest(unittest.TestCase):
    """Tests for the runsteps.Runner Class"""
    def setUp(self):
        """Set some state for each tests in this class"""
        self.steps = ['ls', 'pwd']
        self.keys = ['step', 'start_time', 'end_time', 'duration',
                     'return_code']
        self.runner = runsteps.Runner()
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        """clean up the state after each test"""
        shutil.rmtree(self.tempdir, ignore_errors=True)
        shutil.rmtree(self.runner.datadir, ignore_errors=True)

    def test_init(self):
        """New instances of Runner will have initialized properties"""
        self.assertEqual([], self.runner.history)
        self.assertEqual([], self.runner._steps)

    def test_init_creates_datadir_and_subdirs(self):
        """Ensure that the datadir and subdirs are created"""
        shutil.rmtree(self.runner.datadir, ignore_errors=True)
        runsteps.Runner()
        self.assertTrue(os.path.isdir(self.runner.datadir))
        self.assertTrue(os.path.isdir(self.runner.envdir))
        self.assertTrue(os.path.isdir(self.runner.logdir))

    def test_load_only_allows_lists(self):
        """New instances will raise an Exception if given a non-list object"""
        steps = 'This is not a list'
        with self.assertRaises((runsteps.RunnerException, SystemExit)):
            self.runner.load(steps)

    def test_run_history(self):
        """At the end of a run, the history property should exist and contain a
           list of dicts describing the steps that were executed
        """
        self.runner.load(self.steps)
        self.runner.run()
        num = len(self.steps)
        self.assertEqual(num, len(self.runner.history))
        for i in range(0, num):
            self.assertEqual(self.steps[i], self.runner.history[i]['step'])
            for key in self.keys:
                self.assertTrue(key in self.runner.history[i])

    def test_run_from_a_file_path(self):
        """Call run with the path specified as a file"""
        steps = ['ls', 'pwd', 'env']
        tempfile_name = '/'.join([self.tempdir, 'steps.json'])
        with open(tempfile_name, 'w') as tempfile:
            json.dump(steps, tempfile)
        self.runner.load_from_path(tempfile_name)
        self.runner.run()
        self.assertEqual(steps, self.runner._steps)

    def test_load_from_path_with_a_bad_path(self):
        """Call run with a bad path"""
        with self.assertRaises((runsteps.RunnerException, SystemExit)):
            self.runner.load_from_path('this_is_not_a_file')

    def test_run_creates_logs(self):
        """Test that logfiles are created for each step with appropriate
           output
        """
        files = {'test1.sh': '#!/bin/sh\n'
                             'echo "blah"\n'}
        out = io.StringIO()
        fill_directory(self.tempdir, files)
        self.runner.load_from_path(self.tempdir)
        self.runner.run(out=out)
        logfiles = glob.glob('{}/test1.sh*.log'.format(self.runner.logdir))
        self.assertTrue(logfiles)
        with open(logfiles[0], 'r') as logfile:
            output_fromfile = logfile.read()
        self.assertEqual(output_fromfile, out.getvalue())
        self.assertEqual(output_fromfile, 'blah\n')

    def test_run_without_logs(self):
        """run should not create log files when specified"""
        self.runner.load(self.steps)
        self.runner.run(logs=False)
        self.assertFalse(glob.glob('{}/*.log'.format(self.runner.logdir)))

    def test_run_with_quiet_still_produces_logs(self):
        """Test setting output to None still produces logs"""
        self.runner.load(self.steps)
        self.runner.run(out=None)
        logfiles = glob.glob('{}/*.log'.format(self.runner.logdir))
        self.assertTrue(logfiles)
        with open(logfiles[0], 'r') as logfile:
            output_fromfile = logfile.read()
        self.assertTrue(output_fromfile)

    def test_run_halts_execution_when_a_command_fails(self):
        """run should not execute the rest of the steps when one fails"""
        steps = ['true', 'false', 'ls']
        self.runner.load(steps)
        with self.assertRaises((runsteps.RunnerException, SystemExit)):
            self.runner.run()
        executed_steps = [x['step'] for x in self.runner.history]
        self.assertEqual(['true', 'false'], executed_steps)

    def test_run_inherit_env(self):
        """Test that the step receives existing environment variables when
           inherit_env is true.
        """
        val = ''.join(random.choice(string.ascii_lowercase) for x in range(6))
        os.putenv('RUNSTEPS_TESTENV_VAR', val)
        self.runner.load(self.steps)
        self.runner.run(inherit_env=True)
        self.assertTrue('RUNSTEPS_TESTENV_VAR' in self.runner._env)
        self.assertEqual(self.runner._env['RUNSTEPS_TESTENV_VAR'], val)

    def test_run_saved_keypairs_are_preserved_as_environment_variables(self):
        """Test that environment variables stored as keypairs in the
           RUNSTEPS_DATA directory are passed from step to step.
           Newer steps can overwrite data from previous steps.
        """
        files = {'test1': '#!/bin/sh\n'
                          '. "$RUNSTEPS_ENV/runsteps_helpers.sh"\n'
                          'runsteps_save_keypair RUNSTEPS_TESTING YES\n',
                 'test2': '#!/bin/sh\n'
                          '[ "$RUNSTEPS_TESTING" = "YES" ] || exit 1\n'
                          '. "$RUNSTEPS_ENV/runsteps_helpers.sh"\n'
                          'runsteps_save_keypair RUNSTEPS_TESTING NO\n'
                          'runsteps_save_keypair RUNSTEPS_TESTING MAYBE\n'}
        fill_directory(self.tempdir, files)
        self.runner.load_from_dir(self.tempdir)
        self.runner.run()
        self.assertTrue('RUNSTEPS_TESTING' in self.runner._env)
        self.assertEqual(self.runner._env['RUNSTEPS_TESTING'], 'MAYBE')

    def test_dryrun(self):
        """Test that a dryrun only prints output"""
        self.runner.load(self.steps)
        out = io.StringIO()
        with self.assertRaises(SystemExit):
            self.runner.dryrun(out=out)
        self.assertFalse(self.runner.history)
        output = json.loads(out.getvalue())
        self.assertEqual(output, self.steps)

    def test_dryrun_noout(self):
        """Test dryrun just exits if passed a bad out fd"""
        self.runner.load(self.steps)
        self.runner.dryrun(out=None)

    def test_run_badfiles_are_handled_properly(self):
        """Test that encountering a bad executable raises RunnerException"""
        steps = ['step1.sh', 'step2.sh', 'step3.sh']
        tempfile_name = '/'.join([self.tempdir, 'steps.json'])
        with open(tempfile_name, 'w') as tempfile:
            json.dump(steps, tempfile)
        self.runner.load_from_path(tempfile_name)
        with self.assertRaises((runsteps.RunnerException, SystemExit)):
            self.runner.run(logs=False)
        self.assertTrue(len(self.runner.history) == 1)
        self.assertTrue('step1.sh' == self.runner.history[0]['step'])
        self.assertTrue(
            self.runner.history[0]['return_code'] == 1)

    def test_load_from_dir_fails_on_missing_directory(self):
        """load_from_dir should fail on missing directories"""
        with self.assertRaises(IOError):
            self.runner.load_from_dir('some fake directory')

    def test_load_from_dir_populates_steps(self):
        """load_from_dir will fill self._steps with files found"""
        files = {'one': True, 'two': True, 'three': True}
        paths = fill_directory(self.tempdir, files)
        self.runner.load_from_dir(self.tempdir)
        for step in paths:
            self.assertTrue(step in self.runner._steps)

    def test_load_from_dir_excludes_non_executable_files(self):
        """load_from_dir should only find executable files"""
        files = {'one': True, 'two': False, 'three': True}
        badpath = '/'.join([self.tempdir, 'two'])
        fill_directory(self.tempdir, files)
        self.runner.load_from_dir(self.tempdir)
        self.assertFalse(badpath in self.runner._steps)
        self.assertEqual(len(self.runner._steps), 2)

    def test_load_from_dir_sorts_order_alphabetically(self):
        """load_from_dir should choose order in a predictable way, alphabetically
           ascending
        """
        files = {'03_testing': True, 'aardvark': True, '01_ztesting': True}
        expected = ['{}/01_ztesting'.format(self.tempdir),
                    '{}/03_testing'.format(self.tempdir),
                    '{}/aardvark'.format(self.tempdir)]
        fill_directory(self.tempdir, files)
        self.runner.load_from_dir(self.tempdir)
        self.assertEqual(self.runner._steps, expected)

    def test_load_from_file_populates_steps(self):
        """load_from_file will fill self._steps with data from a json file"""
        steps = ['step1.sh', 'step2.sh', 'step3.sh']
        tempfile_name = '/'.join([self.tempdir, 'steps.json'])
        with open(tempfile_name, 'w') as tempfile:
            json.dump(steps, tempfile)
        self.runner.load_from_file(tempfile_name)
        self.assertEqual(steps, self.runner._steps)

    def test_print_history(self):
        """Test the print history method"""
        self.runner.load(self.steps)
        self.runner.run()
        out = io.StringIO()
        self.runner.print_history(out=out)
        output = out.getvalue()
        self.assertTrue(output is not None)
        self.assertEqual(type(json.loads(output)), type([]))

    def test_print_history_IOError(self):
        """Test that an exit occurs when the history file cannot be read"""
        shutil.rmtree(self.runner.datadir)
        with self.assertRaises((runsteps.RunnerException, SystemExit)):
            self.runner.print_history()

    def test_main_help(self):
        """Execute the main function with the help flag.
           Currently this test is pretty meaningless.
        """
        with self.assertRaises(SystemExit):
            runsteps.main(args=['-h'])

    def test_main_dryrun(self):
        """Execute the main function with the dryrun flag.
           Currently this test is pretty meaningless.
        """
        files = {'test1.sh': '#!/bin/sh\n'
                             'echo "blah"\n'}
        fill_directory(self.tempdir, files)
        with self.assertRaises((SystemExit)):
            runsteps.main(args=['-d', self.tempdir])

    def test_main_verbose(self):
        """Execute the main function with the verbose flag.
           Currently this test is pretty meaningless.
        """
        files = {'test1.sh': '#!/bin/sh\n'
                             'echo "blah"\n'}
        fill_directory(self.tempdir, files)
        runsteps.main(args=['-v', self.tempdir])
