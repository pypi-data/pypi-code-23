from __future__ import print_function

# Test the Open Babel FastSearch .fs interface

import unittest
import os
import gzip
import shutil

import chemfp
from chemfp_converters import fs2fps, fps2fs, __version__ as version
from chemfp_converters import fastsearch

import support

DRUGS_SDF = support.find("drugs.sdf")
DRUGS_FPS = support.find("drugs_openbabel_FP2.fps")
DRUGS_FS = support.find("drugs.fs")

VITAMINS_SMI = support.find("vitamins.smi")
VITAMINS_TAB_SMI_GZ = support.find("vitamins_tab.smi.gz")
VITAMINS_FPS = support.find("vitamins_openbabel_MACCS.fps")
VITAMINS_FS = support.find("vitamins.fs")

_2fps_runner = support.Runner(fs2fps.main)

fs2fps = _2fps_runner.run

def fs2fps_binary_stdout(*args, **kwargs):
    kwargs["binary_stdout"] = True
    stdout, stderr = fs2fps(*args, **kwargs)
    return stdout
    
class TestFS2FPS(unittest.TestCase):
    def test_version(self):
        stdout, stderr = fs2fps(["--version"], should_exit=True)
        terms = stdout.split()
        self.assertEqual(terms[1], version)

    def test_drugs_with_id(self):
        stdout = fs2fps_binary_stdout([DRUGS_FS])
        text = stdout.decode("ascii")
        self.assertIn("\n#num_bits=1021\n", text)
        self.assertIn("\n#type=OpenBabel-FP2/1\n", text)
        self.assertIn("808000000000004\tacetsali\n", text)
        self.assertIn("200000800001880002a000000\tcaffeine\n", text)

        got_date = support.get_date(stdout)
        expected_date = support.get_file_date(DRUGS_FS)
        self.assertEqual(got_date, expected_date)
        
    def test_drugs_with_index(self):
        stdout = fs2fps_binary_stdout([DRUGS_FS, "--use-index-as-id"])
        text = stdout.decode("ascii")
        self.assertIn("\n#num_bits=1021\n", text)
        self.assertIn("\n#type=OpenBabel-FP2/1\n", text)
        self.assertIn("808000000000004\t0\n", text)
        self.assertIn("200000800001880002a000000\t5\n", text)

        got_date = support.get_date(stdout)
        expected_date = support.get_file_date(DRUGS_FS)
        self.assertEqual(got_date, expected_date)
    
    def test_drugs_with_offset(self):
        stdout = fs2fps_binary_stdout([DRUGS_FS, "--use-offset-as-id"])
        text = stdout.decode("ascii")
        self.assertIn("\n#num_bits=1021\n", text)
        self.assertIn("\n#type=OpenBabel-FP2/1\n", text)
        self.assertIn("808000000000004\t0\n", text)
        self.assertIn("200000800001880002a000000\t7542\n", text)

        got_date = support.get_date(stdout)
        expected_date = support.get_file_date(DRUGS_FS)
        self.assertEqual(got_date, expected_date)

    def test_vitamins(self):
        stdout = fs2fps_binary_stdout([VITAMINS_FS])
        text = stdout.decode("ascii")
        self.assertIn("\n#type=OpenBabel-MACCS/2\n", text)
        self.assertNotIn("\n#software=", text)
        self.assertIn(
            "\n"
            "0000000000000200020a020004982c80001434951c\tretinol\n"
            "000000000000300180080685841000440c4da25718\tvitamin C\n"
            "0000000002000200020a008294892cc00954b5941c\tcholecalciferol\n",
            text)

        got_date = support.get_date(stdout)
        expected_date = support.get_file_date(VITAMINS_FS)
        self.assertEqual(got_date, expected_date)

    def test_vitamins_with_type_source_software_and_date(self):
        stdout = fs2fps_binary_stdout(
            [VITAMINS_FS, "--type", "Blah", "--source", "/dev/null",
                 "--software", "ABC/123", "--date", "2000-01-18T01:02:03"])
        text = stdout.decode("ascii")
        self.assertIn("\n#type=Blah\n", text)
        self.assertIn("\n#source=/dev/null\n", text)
        self.assertIn("\n#software=ABC/123\n", text)
        self.assertIn("\n#date=2000-01-18T01:02:03\n", text)

    def test_vitamins_without_type_source_and_date(self):
        stdout = fs2fps_binary_stdout(
            [VITAMINS_FS, "--no-type", "--no-source", "--no-date"])
        text = stdout.decode("ascii")
        self.assertNotIn("\n#type=", text)
        self.assertNotIn("\n#source=", text)
        self.assertNotIn("\n#software=", text)
        self.assertNotIn("\n#date=", text)
        
    def test_bad_date(self):
        stdout, stderr = fs2fps([VITAMINS_FS, "--date", "2003-05-12"], should_exit=True)
        self.assertIn("time data '2003-05-12' does not match format '%Y-%m-%dT%H:%M:%S'", stderr)
        
    def test_dump_vitamins(self):
        stdout, stderr = fs2fps([VITAMINS_FS, "--dump"])
        lines = stdout.splitlines(False)
        self.assertIn("** Header from", lines[0])
        self.assertIn("vitamins.fs", lines[0])
        
        self.assertEqual([
            "Header length: 284",
            "#entries: 3",
            "#words/fp: 8 (#bits/fp: 166)",
            "Open Babel fingerprint type: 'MACCS'",
            "chemfp fingerprint type: 'OpenBabel-MACCS/2'",
            "datafile filename: 'vitamins.smi'",
            "** End of header. Start of fingerprint records.",

            "index\toffset\tfingerprint",
            "0\t0\t0000000000000200020a020004982c80001434951c",
            "1\t51\t000000000000300180080685841000440c4da25718",
            "2\t92\t0000000002000200020a008294892cc00954b5941c",
            ], lines[1:])

    # XXX need to test --output

_2fs_runner = support.Runner(fps2fs.main)

fps2fs = _2fs_runner.run
def fps2fs_binary_stdout(*args, **kwargs):
    kwargs["binary_stdout"] = True
    stdout, stderr = _2fs_runner.run_stdout(*args, **kwargs)
    return stdout

        
class TestFPS2FS(unittest.TestCase):
    def test_version(self):
        stdout, stderr = fps2fs(["--version"], should_exit=True)
        terms = stdout.split()
        self.assertEqual(terms[1], version)

    def test_drugs(self):
        dirname = support.get_tmpdir(self)
        output_filename = os.path.join(dirname, "drugs.fs")
        
        fps2fs(["-d", DRUGS_SDF, DRUGS_FPS, "--output", output_filename])

        # does index lookup work?
        with open(output_filename, "rb") as f:
            with fastsearch.open_index(f, id_type="index") as fs_reader:
                self.assertEqual(fs_reader.data_filename, DRUGS_SDF)
                self.assertEqual(fs_reader.header.num_entries, 6)
                self.assertEqual(fs_reader.header.num_words, 32)
                self.assertEqual(fs_reader.header.fpid, "FP2")

                with chemfp.open(DRUGS_FPS) as fps_reader:
                    expected = [(str(i), fp) for i, (id, fp) in enumerate(fps_reader)]
                    self.assertEqual(list(fs_reader), expected)

        # does id lookup work?
        with fastsearch.open_index(output_filename, id_type="id") as fs_reader:
            with chemfp.open(DRUGS_FPS) as fps_reader:
                self.assertEqual(list(fs_reader), list(fps_reader))
                    
        # does offset lookup work?
        with fastsearch.open_index(output_filename, id_type="offset") as fs_reader:
            expected = ["0", "1200", "2667", "4286", "5837", "7542"]
            self.assertEqual([offset for (offset, fp) in fs_reader], expected)

            
    def test_vitamins(self):
        dirname = support.get_tmpdir(self)
        output_filename = os.path.join(dirname, "vitamins.fs")
        
        fps2fs(["--datafile", VITAMINS_SMI, VITAMINS_FPS, "-o", output_filename])
        
        with fastsearch.open_index(output_filename, id_type="id") as fs_reader:
            self.assertEqual(fs_reader.data_filename, VITAMINS_SMI)
            self.assertEqual(fs_reader.header.num_entries, 3)
            self.assertEqual(fs_reader.header.num_words, 8)
            self.assertEqual(fs_reader.header.fpid, "MACCS")
            
            expected = ["retinol", "vitamin C", "cholecalciferol"]
            self.assertEqual([offset for (offset, fp) in fs_reader], expected)

        with fastsearch.open_index(output_filename, id_type="index") as fs_reader:
            expected = ["0", "1", "2"]
            self.assertEqual([offset for (offset, fp) in fs_reader], expected)

        with fastsearch.open_index(output_filename, id_type="offset") as fs_reader:
            expected = ["0", "51", "92"]
            self.assertEqual([offset for (offset, fp) in fs_reader], expected)

    def test_vitamins_gz_delimiter_and_header(self):
        dirname = support.get_tmpdir(self)
        output_filename = os.path.join(dirname, "vitamins.fs")
        fps_filename = os.path.join(dirname, "vitamins.fps.gz")

        # Create an FPS file with identifiers matching the "space" delimited SMILES
        with open(VITAMINS_FPS, "rb") as f:
            content = f.read()
            lines = content.splitlines(True)
        self.assertEqual(len(lines), 9, (VITAMINS_FPS, lines))
        del lines[-3]
        lines[-2] = lines[-2].replace(b"vitamin C", b"vitamin")

        f = gzip.open(fps_filename, "wb")
        try:
            f.writelines(lines)
        finally:
            f.close()
        
        stdout, stderr = fps2fs(
            ["--datafile", VITAMINS_SMI, "--delimiter", "space", "--has-header",
                fps_filename, "-o", output_filename])
        self.assertTrue(os.path.isfile(output_filename), output_filename)
        
        with fastsearch.open_index(output_filename, id_type="index") as fs_reader:
            expected = ["0", "1"]
            self.assertEqual([index for (index, fp) in fs_reader], expected)

        with fastsearch.open_index(output_filename, id_type="offset") as fs_reader:
            expected = ["51", "92"]
            self.assertEqual([offset for (offset, fp) in fs_reader], expected, output_filename)

        with fastsearch.open_index(output_filename, id_type="id", delimiter="space") as fs_reader:
            self.assertEqual(fs_reader.header.data_filename, VITAMINS_SMI)
            
            expected = ["vitamin", "cholecalciferol"]
            self.assertEqual([id for (id, fp) in fs_reader], expected)

            
    def test_vitamins_tab(self):
        dirname = support.get_tmpdir(self)
        output_filename = os.path.join(dirname, "vitamins.fs")
        
        fps2fs(["--datafile", VITAMINS_TAB_SMI_GZ, VITAMINS_FPS, "--delimiter", "tab", "-o", output_filename])
        
        with fastsearch.open_index(output_filename, id_type="id") as fs_reader:
            expected = ["retinol\tABC", "vitamin C\tDEF", "cholecalciferol\tGHI"]
            self.assertEqual([offset for (offset, fp) in fs_reader], expected)

        with fastsearch.open_index(output_filename, id_type="id", delimiter="tab") as fs_reader:
            expected = ["retinol", "vitamin C", "cholecalciferol"]
            self.assertEqual([offset for (offset, fp) in fs_reader], expected)

        with fastsearch.open_index(output_filename, id_type="index") as fs_reader:
            expected = ["0", "1", "2"]
            self.assertEqual([offset for (offset, fp) in fs_reader], expected)

        with fastsearch.open_index(output_filename, id_type="offset") as fs_reader:
            expected = ["0", "55", "100"]
            self.assertEqual([offset for (offset, fp) in fs_reader], expected)
        
    def test_with_default_output_filename(self):
        dirname = support.get_tmpdir(self)
        fps_filename = os.path.join(dirname, "blah.fps")
        shutil.copy(VITAMINS_FPS, fps_filename)
        stdout, stderr = fps2fs([fps_filename, "--datafile", VITAMINS_SMI])
        self.assertFalse(stdout)
        self.assertIn("WARNING: No --output filename given, using '", stderr)
        self.assertIn("/blah.fs'.\n", stderr)
        self.assertIn("/blah.fs'.\n", stderr)
        self.assertIn("Indexed 3 datafile records.", stderr)
        
    def test_quiet(self):
        dirname = support.get_tmpdir(self)
        fps_filename = os.path.join(dirname, "blah.fps")
        shutil.copy(VITAMINS_FPS, fps_filename)
        stdout, stderr = fps2fs([fps_filename, "--datafile", VITAMINS_SMI, "--quiet"])
        self.assertFalse(stdout)
        self.assertFalse(stderr)
        stdout, stderr = fps2fs([fps_filename, "--datafile", VITAMINS_SMI, "-q"])
        self.assertFalse(stdout)
        self.assertFalse(stderr)
        
        
if __name__ == "__main__":
    unittest.main()
