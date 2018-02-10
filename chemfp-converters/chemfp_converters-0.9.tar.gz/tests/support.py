import sys
import os
import io
import contextlib
import tempfile
import shutil
import datetime

_dirname = os.path.dirname(__file__)

def find(filename):
    path = os.path.join(_dirname, filename)
    if not os.path.exists(path):
        raise AssertionError("Cannot find file %r:" % (path,))
    return path

if sys.version_info < (3, 0, 0):
    import cStringIO
    class CaptureStdout(object):
        def __init__(self, binary_stdout):
            self.binary_file = self.text_file = cStringIO.StringIO()
        def __enter__(self):
            self.old_stdout = sys.stdout
            sys.stdout = self.text_file
            return self.text_file
        def __exit__(self, *args):
            sys.stdout = self.old_stdout
            
    class CaptureStderr(object):
        def __init__(self):
            self.binary_file = self.text_file = cStringIO.StringIO()
        def __enter__(self):
            self.old_stderr = sys.stderr
            sys.stderr = self.text_file
            return self.text_file
        def __exit__(self, *args):
            sys.stderr = self.old_stderr
else:
    class CaptureStdout(object):
        def __init__(self, binary_stdout):
            if binary_stdout:
                self.binary_file = io.BytesIO()
                self.text_file = io.TextIOWrapper(self.binary_file)
            else:
                self.text_file = io.StringIO()
        def __enter__(self):
            self.old_stdout = sys.stdout
            sys.stdout = self.text_file
            return self.text_file
        def __exit__(self, *args):
            sys.stdout = self.old_stdout

    class CaptureStderr(object):
        def __init__(self):
            self.text_file = io.StringIO()
        def __enter__(self):
            self.old_stderr = sys.stderr
            sys.stderr = self.text_file
            return self.text_file
        def __exit__(self, *args):
            sys.stderr = self.old_stderr
        
# wrapper around the main() call
class Runner(object):
    def __init__(self, main):
        self.main = main

    # Pass args to main(), and return (stdout, stderr)
    def run(self, args, should_exit=False, binary_stdout=False):
        if isinstance(args, str):
            args = args.split()

        real_stdout = sys.stdout
        stdout = CaptureStdout(binary_stdout)
        stderr = CaptureStderr()

        try:
            try:
                with stdout:
                    with stderr:
                        self.main(args)

                if should_exit:
                    raise AssertionError("Call should have raised SystemExit")

            except SystemExit as err:
                if not should_exit:
                    ## print("Unexpected SystemExit")
                    ## print(stderr.text_file.getvalue())
                    raise AssertionError("Unexpected SystemExit:\n%s" % (stderr.text_file.getvalue(),))
        except Exception as err:
            ## print("Uncaught exception: %s" % (err,))
            ## print(stderr.text_file.getvalue())
            raise
            

        if binary_stdout:
            return (stdout.binary_file.getvalue(), stderr.text_file.getvalue())
        else:
            return (stdout.text_file.getvalue(), stderr.text_file.getvalue())

    # Pass args to main(), and return stdout
    def run_stdout(self, args, should_exit=False, binary_stdout=False):
        stdout, stderr = self.run(args, should_exit, binary_stdout)
        if stdout == "":
            raise AssertionError("missing stdout from %r" % (args,))
        if stderr != "":
            raise AssertionError("unexpected stdout from %r: %r" % (args, stderr))
        return stdout

    # Pass args to main(), and return stderr
    def run_stderr(self, args, should_exit=False, binary_stdout=False):
        stdout, stderr = self.run(args, should_exit, binary_stdout)
        if stdout:
            raise AssertionError("unexpected stdout from %r: %r" % (args, stdout))
        if not stderr:
            raise AssertionError("missing stdout from %r", (args,))
        return stderr


    # Pass args to main(); argparse should reject an argument and give an error message
    def run_argparse_error(self, args, should_exit=False, binary_stdout=False):
        stderr = self.run_stderr(args, should_exit, binary_stdout)
        if ": error: " not in stderr:
            raise AssertionError("expected argparse to fail with %r: %r" % (args, stderr))
        return stderr

def get_tmpdir(test_case):
    dirname = tempfile.mkdtemp()
    test_case.addCleanup(shutil.rmtree, dirname)
    return dirname

def get_tmpfile(testcase, filename):
    dirname = tempfile.mkdtemp(prefix="chemfp_test")
    testcase.addCleanup(shutil.rmtree, dirname)
    filename = os.path.join(dirname, filename)
    return filename

def get_date(stdout):
    date_line = None
    for line in stdout.splitlines():
        if line.startswith(b"#date="):
            if date_line is None:
                date_line = line
            else:
                raise AssertionError("Muliple dates")
        if line[:1] != b"#":
            break

    if date_line is None:
        return None # missing date
    datetime_str = date_line[6:]
    date_str, _, time_str = datetime_str.partition(b"T")
    year, month, day = date_str.split(b"-")
    hour, minute, second = time_str.split(b":")
    return datetime.datetime(int(year), int(month), int(day),
                             int(hour), int(minute), int(second))
    
def get_file_date(filename):
    file_ctime = os.stat(filename).st_ctime
    creation_datetime = datetime.datetime.utcfromtimestamp(file_ctime)
    return creation_datetime.replace(microsecond=0)
