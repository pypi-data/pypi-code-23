from __future__ import print_function

# Test the interface to Dave Cosgrove's Flush format

import unittest
import datetime

from chemfp_converters import flush2fps, fps2flush, __version__ as version

import support

DRUGS_FLUSH = support.find("drugs.flush")
VITAMINS_FLUSH = support.find("vitamins.flush")

DRUGS_FPS = support.find("drugs_openeye_path.fps")
VITAMINS_FPS = support.find("vitamins_rdkit_morgan.fps")

_2fps_runner = support.Runner(flush2fps.main)

flush2fps = _2fps_runner.run

def flush2fps_binary_stdout(*args, **kwargs):
    kwargs["binary_stdout"] = True
    stdout, stderr = flush2fps(*args, **kwargs)
    return stdout
    
class TestFlush2FPS(unittest.TestCase):
    def test_version(self):
        stdout, stderr = flush2fps(["--version"], should_exit=True)
        terms = stdout.split()
        self.assertEqual(terms[1], version)

    def test_drugs(self):
        stdout = flush2fps_binary_stdout([DRUGS_FLUSH])
        lines = [line for line in stdout.splitlines(True) if not line.startswith(b"#date=")]
        self.assertEqual(lines[0], b"#FPS1\n")
        self.assertEqual(lines[1], b"#num_bits=4096\n")
        del lines[1]
        del lines[0]

        with open(DRUGS_FPS, "rb") as f:
            expected_lines = [line for line in f if line[:1] != b"#"]

        self.assertEqual(lines, expected_lines)

    def test_vitamins(self):
        stdout = flush2fps_binary_stdout([VITAMINS_FLUSH])
        lines = [line for line in stdout.splitlines(True) if not line.startswith(b"#date=")]
        self.assertEqual(lines[0], b"#FPS1\n")
        self.assertEqual(lines[1], b"#num_bits=4096\n")
        del lines[1]
        del lines[0]

        with open(VITAMINS_FPS, "rb") as f:
            expected_lines = [line for line in f if line[:1] != b"#"]

        self.assertEqual(lines, expected_lines)

    def test_default_date(self):
        stdout = flush2fps_binary_stdout([DRUGS_FLUSH])
        got_date = support.get_date(stdout)
        expected_date = support.get_file_date(DRUGS_FLUSH)
        self.assertEqual(got_date, expected_date)

    def test_specified_date(self):
        stdout = flush2fps_binary_stdout([DRUGS_FLUSH, "--date", "1990-08-22T12:34:56"])
        got_date = support.get_date(stdout)
        expected_date = datetime.datetime(1990, 8, 22, 12, 34, 56)
        self.assertEqual(got_date, expected_date)

    def test_no_date(self):
        stdout = flush2fps_binary_stdout([DRUGS_FLUSH, "--no-date"])
        got_date = support.get_date(stdout)
        expected_date = None
        self.assertEqual(got_date, expected_date)
        

_2flush_runner = support.Runner(fps2flush.main)

fps2flush = _2flush_runner.run
    
def fps2flush_binary_stdout(*args, **kwargs):
    kwargs["binary_stdout"] = True
    stdout, stderr = fps2flush(*args, **kwargs)
    return stdout
    
class TestFPS2Flush(unittest.TestCase):
    def test_version(self):
        stdout, stderr = fps2flush(["--version"], should_exit=True)
        terms = stdout.split()
        self.assertEqual(terms[1], version)

    def _convert(self, input_filename, tmp_filename, output_filename):
        filename = support.get_tmpfile(self, tmp_filename)
        stdout, stderr = fps2flush([input_filename, "-o", filename])
        self.assertFalse(stdout)
        self.assertFalse(stderr)

        with open(output_filename, "rb") as f:
            expected = f.read()
        with open(filename, "rb") as f:
            got = f.read()

        self.assertEqual(got, expected)
        
    def test_drugs(self):
        self._convert(DRUGS_FPS, "tmp_drugs.flush", DRUGS_FLUSH)

    def test_vitamins(self):
        self._convert(VITAMINS_FPS, "tmp_vitamins.flush", VITAMINS_FLUSH)

    def test_vitamins_to_stdout(self):
        stdout, stderr = fps2flush([VITAMINS_FPS], binary_stdout=True)
        with open(VITAMINS_FLUSH, "rb") as f:
            expected = f.read()

        self.assertEqual(stdout, expected)
        

if __name__ == "__main__":
    unittest.main()
