from __future__ import print_function

import os
import unittest
import io
import shutil

import chemfp
import chemfp.io
from chemfp import bitops

from chemfp_converters import fps2fpbin, fpbin2fps, __version__ as version
from chemfp_converters import fpbin

import support

has_oegraphsim = False
try:
    from openeye.oechem import OEMolDatabase, OEChemIsLicensed
except ImportError:
    no_oechem = "OEChem Python libraries not installed"
else:
    if OEChemIsLicensed():
        no_oechem = None
    else:
        no_oechem = "OEChem Python license not valid"
    from openeye.oegraphsim import OEGraphSimIsLicensed, OEGetFPType
    has_oegraphsim = OEGraphSimIsLicensed()
    

        
_2fps_runner = support.Runner(fpbin2fps.main)
fpbin2fps = _2fps_runner.run

DRUGS_FPBIN = support.find("drugs.fpbin")
DRUGS_SDF = support.find("drugs.sdf")
DRUGS_FPS = support.find("drugs_openeye_path.fps")

VITAMINS_FPBIN = support.find("vitamins.fpbin")
VITAMINS_SMI = support.find("vitamins.smi")
VITAMINS_FPS = support.find("vitamins_openeye_circular.fps")

DRUGS_FINGERPRINTS = (
    b'00000000200000000000000008000000000000000000000408'
    b'00000000000000000000000000000000000000000000000000'
    b'00010000000000000000000000000000000000000008000000'
    b'00000100000000000000080000000001000000000040000000'
    b'00000000000000000000020000080000000000008200200000'
    b'00000000000000000000000000400000000000200080000008'
    b'00000000002000000000000020000000000080000000004000'
    b'00000100001000000100204000210000200000000080000000'
    b'00000000200000400000000000020001000000000000088000'
    b'00000000000100000000000080000000010000000008012000'
    b'00000000000000800000000000000000010200100001000000'
    b'00000000000000000000000000000000000000800800000008'
    b'00000000000000000000000000004000000000000000004000'
    b'00000000000000000000000000000000000000000000000000'
    b'00000008000000000002000000000010208000000000000000'
    b'00000020000000400000000100840080000000800080080000'
    b'00000006000400000000000000000000000000000200000000'
    b'00040000000001000000000200000000000000000000000800'
    b'00400000000000400000000000040000000000010000000000'
    b'00000000000000000000000002000000000000000000000000'
    b'000000000004000004000000\tacetsali\n0000001000008000'
    b'00000000800000804000000000000060000000000000000000'
    b'00000000080000000000000000000004080000080000000000'
    b'01000000008000040000000000000000002200000000000400'
    b'00100000000000000800000000000000000000240000000000'
    b'0024020000000000000010000000a000080000000000000000'
    b'01000080000002000000000600020000080000802000000200'
    b'0000000000000000000800000000000000000a000000100000'
    b'00000002000000000200000040200000100000000008000000'
    b'88000010002000002020000000040000100900000000000000'
    b'00000100000000000800000000010000100000000a00000000'
    b'00000000000000000000000000000000080000000000000000'
    b'00000000000000008000804004000000000000000000000016'
    b'00000004000000000000000040000008008010000000000000'
    b'00000000000000000000000210120000100002000200000000'
    b'00000200000800000084000020000010100008000000000000'
    b'00000000200000800000000000000000000000010000010a00'
    b'00000800000000000000410200010000000008000000000000'
    b'00000000000008080000000000000000000040000000800000'
    b'00004000000000000000000000000000000100010000000000'
    b'00002000000000000000000000000000a00000000000004000'
    b'00000000\tacyclovi\n00000000000000000000000000000000'
    b'00001000000000000000000000080000000000000020000000'
    b'00200010000000004020010000000000000000000000000010'
    b'00000000000000004000000000020000000000000000000000'
    b'00000000004000000000000401000000000000010000000020'
    b'00010000000020000800000000000000000002000000000000'
    b'00000420000000000810004000002000000000000000000000'
    b'00000008020000000002000000000000000100000108000000'
    b'00000000000020000000008000200000004000000000000001'
    b'00000000000008800000000000000100000000000000000000'
    b'01000000000000000000000000020000000000000000000000'
    b'00000000000100000000000000000100000000200002040000'
    b'00000080880000000040000000000040020000010000004010'
    b'00000000000000400800000000008000000002000000000004'
    b'04000000000000400000000809000000000000000000000000'
    b'20800000000020000000040800000000000000000100000080'
    b'00000000000020080000600002000008014000000000000000'
    b'00000000000000010000000008600000000080000000100004'
    b'00000000000000000000400000000000400000000200040000'
    b'00010000000000000000000000000000000000000000000020'
    b'100000000001000004000000000100000004000010\talpreno'
    b'l\n000000000001002000000000000000000002010000020100'
    b'00000000000000010000000000000020000000000000000000'
    b'00000004000080080208000000002000000003000000100400'
    b'00000000000000444000000000000800000000000000000000'
    b'00000020000000000000000000000000000000000000002000'
    b'00000001000000000000000800400000000080000000020000'
    b'80000000000000001000001000000200200008000008000802'
    b'00000000000010008100020000000000000200000040200000'
    b'00000010002000080000000000000000010000000000800880'
    b'00000000000100000000000000000204000100000000400000'
    b'00000000200000000000080000001000000000400000804800'
    b'00000000000000001000002000008000008000000000080000'
    b'00010000000000000080000000000000000000000040040000'
    b'00000800020008800000000000000000000010008000000000'
    b'80188000000000002000000000000000002080000000000000'
    b'00000000000000000000000001000002000000100000200040'
    b'00000000000000000000000000000000000000020000000000'
    b'00000008000000000000000000200001000000000000000300'
    b'00004002800200080000000008000400020000800000000000'
    b'00100000400000000081200400001000020000010000000200'
    b'20000000000000000010000000\taminopy\n000004000000000'
    b'00000000000000001000010000000000000000000000000000'
    b'00000000020000000002000100000000040000000000000000'
    b'00000000000040010000000000800400040000000000200000'
    b'00000000000001000000000000100000000000004000000000'
    b'00000000000000020000100000000200008000000000000000'
    b'80002000000000000000000000000100008100040000000000'
    b'00000000000000000000000080000004000000000000010000'
    b'00000000000000000000000000000200000000000002000002'
    b'04000000000000001000000000000000000000000000000010'
    b'00000000000010000010000000000000000000000000000000'
    b'00000000020000000010000000000000000000000000000000'
    b'00000200000040000000000000000000000400000000000400'
    b'20000010000004010000000000000000008000000000008000'
    b'00000000000200000000000008000000010100008090000000'
    b'00000000000000000008000000000200002000408000000000'
    b'00080000100800080000000000000200800004000000000080'
    b'14400000000000000000000000000000100000000000000000'
    b'00002000000100000000000000000000000002000000000004'
    b'01000000000000000000100000000000000000000000000000'
    b'00000800000000020000001000000000104000000000000000'
    b'000000000\tatenolol\n0000002000000000000000000000000'
    b'00000000000000000000020000000000000000000008000000'
    b'00120000000000000001000000000000000080000000060000'
    b'40000000040000000000200000000000400001000000400000'
    b'00000000000000000000800204000000000000400000000000'
    b'00000000000002000000002000000008000010000000000220'
    b'00000000000020004000000000000000210000000200000010'
    b'00008000000000002000002000001100000000000000000000'
    b'00000000040200000100000001020000000000000100000000'
    b'02400100000040000004000000000000000000000000000000'
    b'00000000000840000000000000000000000000000002800000'
    b'40000000000000008000000000000100000000000000012000'
    b'48000000000000040000000000000000400020400000000080'
    b'00000000041000000000000000000008000000020400000000'
    b'01010000000100000000002100200000000008000000008000'
    b'000c0000000000000000000000000000000000000002000008'
    b'00080000000200000000010000000000200000000000000100'
    b'00000000001010020000008000000000000000000000080000'
    b'00000000002000001000040000000000000000000000400001'
    b'88000000000000000000000000000001000000000000000000'
    b'2000000000000000020000010000000000000000000\tcaffei'
    b'ne\n')
    
class TestFPBin2FPS(unittest.TestCase):
    def test_version(self):
        stdout, stderr = fpbin2fps(["--version"], should_exit=True)
        terms = stdout.split()
        self.assertEqual(terms[1], version)

    @unittest.skipIf(no_oechem, no_oechem)
    def test_drugs(self):
        stdout, stderr = fpbin2fps([DRUGS_FPBIN], binary_stdout=True)

        arena = chemfp.load_fingerprints(io.BytesIO(stdout), reorder=False)
        metadata = arena.metadata
        self.assertEqual(metadata.num_bits, 4096)
        self.assertEqual(metadata.type,
             "OpenEye-Tree/2 numbits=4096 minbonds=0 maxbonds=4 atype=Arom|AtmNum|Chiral|FCharge|HvyDeg|Hyb btype=Order")
        self.assertIn("drugs.sdf", metadata.sources[0])

        got_date = support.get_date(stdout)
        expected_date = support.get_file_date(DRUGS_FPBIN)
        self.assertEqual(got_date, expected_date)
        
        self.assertEqual(len(arena), 6)
        n = len(DRUGS_FINGERPRINTS)
        fps_text = stdout[-n:]
        for i in range(0, n, 50):
            self.assertEqual(fps_text[i:i+50], DRUGS_FINGERPRINTS[i:i+50], i)

    def test_drugs_keep_type_use_index_as_id(self):
        stdout, stderr = fpbin2fps([DRUGS_FPBIN, "--keep-type", "--use-index-as-id"], binary_stdout=True)
        arena = chemfp.load_fingerprints(io.BytesIO(stdout), reorder=False)
        self.assertEqual(arena.metadata.type,
             "Tree,ver=2.0.0,size=4096,bonds=0-4,atype=AtmNum|Arom|Chiral|FCharge|HvyDeg|Hyb,btype=Order")

        self.assertEqual(arena.ids, ["0", "1", "2", "3", "4", "5"])
        expected = (DRUGS_FINGERPRINTS
                        .replace(b"acetsali", b"0")
                        .replace(b"acyclovi", b"1")
                        .replace(b"alprenol", b"2")
                        .replace(b"aminopy", b"3")
                        .replace(b"atenolol", b"4")
                        .replace(b"caffeine", b"5"))
        self.assertEqual(stdout[-len(expected):], expected)

    @unittest.skipIf(no_oechem, no_oechem)
    def test_drugs_with_output(self):
        filename = support.get_tmpfile(self, "output.fps.gz")
        stdout, stderr = fpbin2fps([DRUGS_FPBIN, "--output", filename])
        self.assertFalse(stdout)
        self.assertFalse(stderr)
        import gzip
        with gzip.open(filename) as f:
            line = f.readline()
        self.assertEqual(line, b"#FPS1\n")
        arena = chemfp.load_fingerprints(filename, reorder=False)
        self.assertEqual(arena.ids, ["acetsali", "acyclovi", "alprenol", "aminopy", "atenolol", "caffeine"])
        
    @unittest.skipIf(no_oechem, no_oechem)
    def test_vitamins(self):
        stdout, stderr = fpbin2fps([VITAMINS_FPBIN], binary_stdout=True)
        arena = chemfp.load_fingerprints(io.BytesIO(stdout), reorder=False)
        self.assertEqual(arena.metadata.type,
             "OpenEye-Path/2 numbits=1024 minbonds=1 maxbonds=3 atype=AtmNum|Chiral|EqHalo|FCharge|HvyDeg|Hyb btype=Order")

        self.assertEqual(len(arena), 3)
        self.assertEqual(arena[0],
         (u"retinol",
          b'\x08 \x000\x00\x00\x04\x00\x00\x02\x08\x00\x00\x01Q\x00(\x00\x01\x00'
          b'\x00\xa0\x00\x02\xa2"\x00\x00\x00@@\x00\x00\x00\x01\x00\x00\x00\x00\x00'
          b'\x04\x00\x00\x04\x00\x00\x02\x1a\x80\x16\x08\x01\x8a\x01\x00\x03\x80$\x00h'
          b'\x00\x00\x01@\x80\x08\x00\x10@@\x02\x10\x14\x00\x08\x00\x81$\x88\x00'
          b'\x06\x00\x02B\x08\x00$\x00\x01!\x00\x10\x00\x00\x80\x00\x10\x00\x02\x08'
          b'\x00\n\x00\x00\x04\x01 \x84\x00\x10\x80\x10@\x80\x00\x04\x80!\x08\x01'
          b'\x80\x00\x04\x00\x00\x05\x10\x10'))
        self.assertEqual(arena[1],
         (u"vitamin C",
          b'\x00\x01\x00\x00\x00@\x0c\x08\x00\x82\x02\x00\xc2\x00 \x00\x90\x80\x01\x00'
          b'\x00\x08\x10\x80\x00\x00\x01\x08\x80@\x01\x00\x00\x01 \x00\x10 \x00\x00'
          b'\x02\x00\x10\x00 \x02\x02\x08\x00\x00\x80\x00\x82\x0c\x02\x00'
          b'\x10\x00\x00\x04\x10 \x80\x11\x01\x00\x10\x08\x80\xb0\x00\x00\x08H\xc0\x00'
          b'\t\x01\x00\x10\x00\x04(\x00\x00\x00\x80(\x00\x08H\x00\x00\x08\x00\x00'
          b'\x00\x00\x00\x04\x08\x00\x00 \x00\x00\x90\x00\x00\x00\x01\x00\x80 \x08\x80'
          b'  \x10\x80@\x00\x00\x00\x08\x01\x02\x10'))
        self.assertEqual(arena[2],
         (u"cholecalciferol",
          b'\x10\x00\x08\x00\x02\x02\x00\x00\x04\x90\x00\x00H\x00\x08\x80\x04\x04 \x81'
          b'\x00\x80\x00\x06\xd0\x02J\x80\x00\x03\x00\x01&\x00@ \x80"\x00\x04'
          b'\x02\x00\x10\x001@\x08\xb2\x00\x04\x00\x04\x02\x10\xc4\x0e\x00\x80\x80\x00'
          b'D\x00\x19\x00\x88\x04,\x1cE@\x04\x00\x01\x10\xa1#,\x84\x00B\x00DA\x10@ \xd1"'
          b'\x00@\x00\x10\x10\x04\x10\x00\x02\xc0@\x84@\x01\x05 \x08\x00$\x00'
          b'\x10\x10\x01\x00\x81\xc3\x00\x89\x01P\x08@\xccBD\x04\x00\x83\n\x00'))

    def test_vitamins_use_index_as_id(self):
        stdout, stderr = fpbin2fps([VITAMINS_FPBIN, "--use-index-as-id"], binary_stdout=True)
        arena = chemfp.load_fingerprints(io.BytesIO(stdout), reorder=False)
        self.assertEqual(arena.metadata.type,
             "OpenEye-Path/2 numbits=1024 minbonds=1 maxbonds=3 atype=AtmNum|Chiral|EqHalo|FCharge|HvyDeg|Hyb btype=Order")
        self.assertEqual(arena.ids, ["0", "1", "2"])

    def test_vitamins_keep_type(self):
        stdout, stderr = fpbin2fps([VITAMINS_FPBIN, "--keep-type", "--use-index-as-id"], binary_stdout=True)
        arena = chemfp.load_fingerprints(io.BytesIO(stdout), reorder=False)
        self.assertEqual(arena.metadata.type,
             "Path,ver=2.0.0,size=1024,bonds=1-3,atype=AtmNum|Chiral|FCharge|HvyDeg|Hyb|EqHalo,btype=Order")

    @unittest.skipIf(no_oechem, no_oechem)
    def test_vitamins_with_moldb(self):
        filename = support.get_tmpfile(self, "fake.smi")
        # Write a SMILES file with 3 lines
        with open(filename, "w") as f:
            f.write("C methane\n")
            f.write("O water\n")
            f.write("O=O molecular oxygen\n")

        stdout, stderr = fpbin2fps([VITAMINS_FPBIN, "--moldb", filename], binary_stdout=True)
        arena = chemfp.load_fingerprints(io.BytesIO(stdout), reorder=False)
        self.assertEqual(arena.ids, ["methane", "water", "molecular oxygen"])

    @unittest.skipIf(no_oechem, no_oechem)
    def test_vitamins_with_wrong_moldb(self):
        filename = support.get_tmpfile(self, "fake.smi")
        # Write a SMILES file with 2 lines
        with open(filename, "w") as f:
            f.write("C methane\n")
            f.write("O=O molecular oxygen\n")

        stdout, stderr = fpbin2fps([VITAMINS_FPBIN, "--moldb", filename],
                                   binary_stdout=True, should_exit=True)
        self.assertIn("Size mismatch: fpbin file ", stderr)
        self.assertIn("vitamins.fpbin' contains 3 fingerprints while moldb file ", stderr)
        self.assertIn("fake.smi' contains 2 molecules\n", stderr)
            
_2fpbin_runner = support.Runner(fps2fpbin.main)
fps2fpbin = _2fpbin_runner.run

class TestFPS2FPBin(unittest.TestCase):
    def test_version(self):
        stdout, stderr = fps2fpbin(["--version"], should_exit=True)
        terms = stdout.split()
        self.assertEqual(terms[1], version)

    def test_drugs(self):
        dirname = support.get_tmpdir(self)
        output_filename = os.path.join(dirname, "test_drugs.fpbin")

        fps2fpbin(["--moldb", DRUGS_SDF, DRUGS_FPS, "--output", output_filename])

        with open(output_filename, "rb") as f:
            output = f.read()

        loc = chemfp.io.Location()
        with fpbin.read_fpbin_records(output_filename, location=loc) as reader:
            h = reader.fpbin_header
            self.assertEqual(h.moldb_filename, DRUGS_SDF)
            self.assertEqual(
                h.oetype_str,
                "Path,ver=2.0.0,size=4096,bonds=0-5,atype=AtmNum|Arom|Chiral|FCharge|HvyDeg|Hyb|EqHalo,btype=Order|Chiral")
            self.assertEqual(h.num_fingerprints, 6)

            self.assertEqual(loc.record_format, "fpbin")
            got_fps = []
            for expected_recno, term in enumerate(reader, 1):
                self.assertEqual(loc.recno, expected_recno)
                index, popcnt, fp = term
                self.assertEqual(index, expected_recno-1)
                start, end = loc.offsets
                record = output[start:end]
                self.assertEqual(start, output.index(record))
                self.assertEqual(end-start, len(record))
                self.assertEqual(loc.record, record)
                self.assertEqual(record[-len(fp):], fp)

                self.assertEqual(popcnt, bitops.byte_popcount(fp))
                
                got_fps.append(fp)

            with chemfp.open(DRUGS_FPS) as f:
                expected_fps = [fp for (id, fp) in f]
                
            self.assertEqual(got_fps, expected_fps)

    def test_vitamins(self):
        dirname = support.get_tmpdir(self)
        output_filename = os.path.join(dirname, "test_vitamin.fpbin")

        fps2fpbin(["--moldb", VITAMINS_SMI, VITAMINS_FPS, "--output", output_filename])

        loc = chemfp.io.Location()
        with fpbin.read_fpbin_records(output_filename, location=loc) as reader:
            h = reader.fpbin_header
            self.assertEqual(h.moldb_filename, VITAMINS_SMI)
            self.assertEqual(
                h.oetype_str,
                "Circular,ver=2.0.0,size=512,radius=0-3,atype=AtmNum|Arom|Chiral|FCharge|HvyDeg|Hyb|InRing|"
                "HCount|EqArom|EqHalo|EqHBAcc|EqHBDon,btype=Order|InRing"
                )
            self.assertEqual(h.num_fingerprints, 3)

            terms = list(reader)
            indices = [term[0] for term in terms]
            self.assertEqual(indices, [0, 1, 2])
            
            got_fps = [term[2] for term in terms]
            with chemfp.open(VITAMINS_FPS) as f:
                expected_fps = [fp for (id, fp) in f]
            self.assertEqual(got_fps, expected_fps)

            got_fps = [term[1] for term in terms]
            expected_fps = [bitops.byte_popcount(fp) for fp in expected_fps]
            self.assertEqual(got_fps, expected_fps)

    def test_vitamins_fp_length_not_multiple_of_8_no_type(self):
        dirname = support.get_tmpdir(self)
        fps_filename = os.path.join(dirname, "input.fps")
        with open(fps_filename, "w") as f:
            f.write("0000000800000200020a020004982c000014301418\tretinol\n")
        output_filename = os.path.join(dirname, "output.fpbin")
        
        stdout, stderr = fps2fpbin(
            ["--moldb", VITAMINS_SMI, fps_filename, "-o", output_filename],
            should_exit=True)
        self.assertFalse(stdout)
        self.assertIn("The fpbin format requires fingerprint sizes which are a multiple of 8 bytes long.\n"
                      "Input has 21 bytes per fingerprint.\n", stderr)

    def test_vitamins_fp_length_not_multiple_of_8_with_type(self):
        dirname = support.get_tmpdir(self)
        fps_filename = os.path.join(dirname, "input.fps")
        with open(fps_filename, "w") as f:
            f.write("#type=OpenEye-MACCS166/3\n")
            f.write("0000000800000200020a020004982c000014301418\tretinol\n")
        output_filename = os.path.join(dirname, "output.fpbin")
        
        stdout, stderr = fps2fpbin(
            ["--moldb", VITAMINS_SMI, fps_filename, "-o", output_filename],
            should_exit=True)
        self.assertFalse(stdout)
        self.assertIn("The fpbin format requires fingerprint sizes which are a multiple of 8 bytes long.\n"
                      "Input type 'OpenEye-MACCS166/3' has 21 bytes per fingerprint.\n", stderr)

    def _internal_test_vitamins_match_moldb(self, quiet):
        dirname = support.get_tmpdir(self)
        moldb_filename = os.path.join(dirname, "moldb.smi")
        # This has an extra struture and missing structure compared to VITAMINS_FPS
        with open(moldb_filename, "w") as f:
            f.write("OC/C=C(C)/C=C/C=C(C)/C=C/C1=C(C)/CCCC1(C)C\tretinol\n"
                    "O[C@@H]1CC(\C(=C)CC1)=C\C=C2/CCC[C@]3([C@H]2CC[C@@H]3[C@H](C)CCCC(C)C)C\tcholecalciferol\n"
                    "C\tmethane\n")
            
        output_filename = os.path.join(dirname, "output.fpbin")

        args = ["--moldb", moldb_filename, VITAMINS_FPS, "--match-moldb", "-o", output_filename]
        if quiet:
            args.append("--quiet")
        stdout, stderr = fps2fpbin(args)
        self.assertFalse(stdout)
        if quiet:
            self.assertFalse(stderr)
        else:
            self.assertTrue(stderr)
            self.assertIn("No fingerprint found for 'methane' (#2).\n", stderr)
            self.assertIn("\nMissing identifiers for 1 of 3 records.\n", stderr)

        # Make sure the fingerprints are correct, including all NULs for the 'methane' entry
        with fpbin.read_fpbin_fingerprints(output_filename) as reader:
            records = list(reader)
            self.assertEqual(len(records), 3)
            self.assertEqual(records[0], (u"retinol",
                b'\x00\x00\x00\x00\x08\x10\x02\x01PH\x00`\x00\x00\x00\x00\x04\x00\x04J'
                b'\x04\x10\x00\x05\x11\x00\x00\x08\x00\x00\x00P\x00\x00p\x10\x00\x00 \x80'
                b'\xc0(\x10\x80\x10@\x00\x8a\x00\x00 \x00\xa0\x00(\x10\x00@ \x10\x00P\x00\x00'))
            self.assertEqual(records[1], (u"cholecalciferol",
                b'\x01D\x81\x00\x83(\x00\x11@\x00\x00D@\x02\r\x01\x81\x00D\x04\x10\x00 \x00'
                b'\x03"!\x00\x08@\x00\x08\xa0\x00@\x00\x00(\x05\xb0`\x00\x04\x80'
                b'\x00\x80\x10\x00\x00\x80\x00@!)A\x14@D@\x00\x85\x10\x01\x02'))
            self.assertEqual(records[2], (u"methane", b"\0"*64))

    @unittest.skipIf(no_oechem, no_oechem)
    def test_vitamins_match_moldb(self):
        self._internal_test_vitamins_match_moldb(quiet=False)
        
    @unittest.skipIf(no_oechem, no_oechem)
    def test_vitamins_match_moldb_quiet(self):
        self._internal_test_vitamins_match_moldb(quiet=True)
            
    def test_with_oechem_type_and_default_output_filename(self):
        dirname = support.get_tmpdir(self)
        fps_filename = os.path.join(dirname, "oechem_type.fps")
        with open(VITAMINS_FPS) as f, open(fps_filename, "w") as g:
            for line in f:
                if line.startswith("#type="):
                    g.write("#type=Tree,ver=2.0.0,size=4096,bonds=3-8,atype=HCount|EqHalo,btype=Chiral\n")
                else:
                    g.write(line)
        stdout, stderr = fps2fpbin(["--moldb", VITAMINS_SMI, fps_filename])
        self.assertFalse(stdout)
        self.assertIn("WARNING: No --output filename given, using ", stderr)
        self.assertNotIn("u'", stderr) # Make sure it doesn't have a b""/u"" prefix
        self.assertNotIn("b'", stderr)
        
        output_filename = os.path.join(dirname, "oechem_type.fpbin")
        self.assertIn(output_filename, stderr)
        
        with fpbin.read_fpbin_records(output_filename) as reader:
            records = list(reader)
        self.assertEqual(len(records), 3)

        
    def test_with_default_output_filename_quiet(self):
        dirname = support.get_tmpdir(self)
        fps_filename = os.path.join(dirname, "oechem_type.fps")
        shutil.copy(VITAMINS_FPS, fps_filename)
        stdout, stderr = fps2fpbin(["--moldb", VITAMINS_SMI, fps_filename, "--quiet"])
        self.assertFalse(stdout)
        self.assertFalse(stderr)
        
        output_filename = os.path.join(dirname, "oechem_type.fpbin")
        with fpbin.read_fpbin_records(output_filename) as reader:
            records = list(reader)
        self.assertEqual(len(records), 3)

                                  

from chemfp_converters.fpbin import CircularFPType, PathFPType, TreeFPType

class TestTypeConversion(unittest.TestCase):
    def _do_tests(self, test_cases):
        for oe_type, type_obj, chemfp_type in test_cases:
            new_obj = fpbin.parse_oetype_string(oe_type)
            self.assertEqual(new_obj, type_obj)
            self.assertEqual(new_obj.to_oetype(), oe_type)
            self.assertEqual(new_obj.to_chemfp_type(), chemfp_type)
            del new_obj
            
            newer_obj = fpbin.parse_chemfp_type_string(chemfp_type)
            self.assertEqual(newer_obj.to_oetype(), oe_type)
            self.assertEqual(newer_obj.to_chemfp_type(), chemfp_type)

            if has_oegraphsim:
                #print("Convert:", repr(oe_type))
                self.assertEqual(OEGetFPType(oe_type).GetFPTypeString(), oe_type)
            
    def _check_atypes(self, fp_func):
        # Iterate through all of the possible atom types
        for atype_shift in range(-1, 13):
            if atype_shift == -1:
                atype = 0
            elif atype_shift == 11:
                continue
            else:
                atype = 1 << atype_shift
            #print("Testing 1 <<", atype_shift, end="")
            oe_type = fp_func(atype).GetFPTypeString()
            type_obj = fpbin.parse_oetype_string(oe_type)
            if atype == 0:
                self.assertEqual(type_obj.atype_terms, [])
            else:
                self.assertEqual(len(type_obj.atype_terms), 1, type_obj.atype_terms)
            self.assertEqual(type_obj.to_oetype(), oe_type)

            chemfp_type = type_obj.to_chemfp_type()
            new_type_obj = fpbin.parse_chemfp_type_string(chemfp_type)
            self.assertEqual(new_type_obj, type_obj)
            self.assertEqual(new_type_obj.to_oetype(), oe_type)
            ## if atype != 0:
            ##     self.assertEqual(chemfp.get_fingerprint_type(chemfp_type).get_type(), chemfp_type)
            
    def _check_btypes(self, fp_func):
        # Iterate through all of the possible bond types
        for btype in (0, 1, 2, 4):
            #print("Testing btype", btype)
            oe_type = fp_func(btype).GetFPTypeString()
            type_obj = fpbin.parse_oetype_string(oe_type)
            if btype == 0:
                self.assertEqual(type_obj.btype_terms, [])
            else:
                self.assertEqual(len(type_obj.btype_terms), 1, type_obj.btype_terms)
            self.assertEqual(type_obj.to_oetype(), oe_type)

            chemfp_type = type_obj.to_chemfp_type()
            new_type_obj = fpbin.parse_chemfp_type_string(chemfp_type)
            self.assertEqual(new_type_obj, type_obj)
            self.assertEqual(new_type_obj.to_oetype(), oe_type)
            ## if btype != 0:
            ##     self.assertEqual(chemfp.get_fingerprint_type(chemfp_type).get_type(), chemfp_type)
                                                        
    def test_path(self):
        test_cases = [
            ("Path,ver=2.0.0,size=4096,bonds=0-5,atype=AtmNum|Arom|Chiral|FCharge|HCount|EqHalo,btype=Order",
             PathFPType("2.0.0", 4096, minbonds=0, maxbonds=5,
                            atype_terms = ["AtmNum", "Arom", "Chiral", "FCharge", "HCount", "EqHalo"],
                            btype_terms = ["Order"]),
             "OpenEye-Path/2 numbits=4096 minbonds=0 maxbonds=5 atype=Arom|AtmNum|Chiral|EqHalo|FCharge|HCount btype=Order"),
             
            ("Path,ver=2.0.0,size=1024,bonds=1-4,atype=AtmNum,btype=None",
             PathFPType("2.0.0", 1024, minbonds=1, maxbonds=4,
                            atype_terms = ["AtmNum"],
                            btype_terms = []),
             "OpenEye-Path/2 numbits=1024 minbonds=1 maxbonds=4 atype=AtmNum btype=0"),

            ("Path,ver=2.0.0,size=512,bonds=2-9,atype=None,btype=Chiral|InRing",
             PathFPType("2.0.0", 512, minbonds=2, maxbonds=9,
                            atype_terms = [],
                            btype_terms = ["InRing", "Chiral"]),
             "OpenEye-Path/2 numbits=512 minbonds=2 maxbonds=9 atype=0 btype=Chiral|InRing"),

             ]
        self._do_tests(test_cases)

    @unittest.skipUnless(has_oegraphsim, "OEGraphSim either not available or not licensed")
    def test_path_enumeration(self):
        from openeye.oegraphsim import OEGetPathFPType
        for numbits, minbonds, maxbonds in ((2**5, 0, 3), (2**6, 0, 0), (2**14, 3, 4), (2**15, 5, 10)):
            # 4, 4 is "atype=Chiral,btype=InRing"
            oe_type = OEGetPathFPType(numbits, minbonds, maxbonds, 4, 4).GetFPTypeString()
            new_obj = fpbin.parse_oetype_string(oe_type)
            self.assertEqual(new_obj.size, numbits)
            self.assertEqual(new_obj.minbonds, minbonds)
            self.assertEqual(new_obj.maxbonds, maxbonds)

        def make_path_atype(atype):
            return OEGetPathFPType(1024, 0, 4, atype, 4)
        self._check_atypes(make_path_atype)

        def make_path_btype(btype):
            return OEGetPathFPType(1024, 0, 4, 4, btype)
        self._check_btypes(make_path_btype)

    def test_tree(self):
        test_cases = [
            ("Tree,ver=2.0.0,size=4096,bonds=0-5,atype=AtmNum|Arom|Chiral|FCharge|HCount|EqHalo,btype=Order",
             TreeFPType("2.0.0", 4096, minbonds=0, maxbonds=5,
                            atype_terms = ["AtmNum", "Arom", "Chiral", "FCharge", "HCount", "EqHalo"],
                            btype_terms = ["Order"]),
             "OpenEye-Tree/2 numbits=4096 minbonds=0 maxbonds=5 atype=Arom|AtmNum|Chiral|EqHalo|FCharge|HCount btype=Order"),
             
            ("Tree,ver=2.0.0,size=1024,bonds=1-4,atype=AtmNum,btype=None",
             TreeFPType("2.0.0", 1024, minbonds=1, maxbonds=4,
                            atype_terms = ["AtmNum"],
                            btype_terms = []),
             "OpenEye-Tree/2 numbits=1024 minbonds=1 maxbonds=4 atype=AtmNum btype=0"),

            ("Tree,ver=2.0.0,size=512,bonds=2-9,atype=None,btype=Chiral|InRing",
             TreeFPType("2.0.0", 512, minbonds=2, maxbonds=9,
                            atype_terms = [],
                            btype_terms = ["InRing", "Chiral"]),
             "OpenEye-Tree/2 numbits=512 minbonds=2 maxbonds=9 atype=0 btype=Chiral|InRing"),

             ]
        self._do_tests(test_cases)

    @unittest.skipUnless(has_oegraphsim, "OEGraphSim either not available or not licensed")
    def test_tree_enumeration(self):
        from openeye.oegraphsim import OEGetTreeFPType
        for numbits, minbonds, maxbonds in ((2**5, 0, 3), (2**6, 0, 0), (2**14, 3, 4), (2**15, 5, 10)):
            # 4, 4 is "atype=Chiral,btype=InRing"
            oe_type = OEGetTreeFPType(numbits, minbonds, maxbonds, 4, 4).GetFPTypeString()
            new_obj = fpbin.parse_oetype_string(oe_type)
            self.assertEqual(new_obj.size, numbits)
            self.assertEqual(new_obj.minbonds, minbonds)
            self.assertEqual(new_obj.maxbonds, maxbonds)

        def make_tree_atype(atype):
            return OEGetTreeFPType(1024, 0, 4, atype, 4)
        self._check_atypes(make_tree_atype)

        def make_tree_btype(btype):
            return OEGetTreeFPType(1024, 0, 4, 4, btype)
        self._check_btypes(make_tree_btype)


    def test_circular(self):
        test_cases = [
            ("Circular,ver=2.0.0,size=4096,radius=0-5,atype=AtmNum|Arom|Chiral|FCharge|HCount|EqHalo,btype=Order",
             CircularFPType("2.0.0", 4096, minradius=0, maxradius=5,
                                atype_terms = ["AtmNum", "Arom", "Chiral", "FCharge", "HCount", "EqHalo"],
                                btype_terms = ["Order"]),
             "OpenEye-Circular/2 numbits=4096 minradius=0 maxradius=5 atype=Arom|AtmNum|Chiral|EqHalo|FCharge|HCount btype=Order"),
             
            ("Circular,ver=2.0.0,size=1024,radius=1-4,atype=AtmNum,btype=None",
             CircularFPType("2.0.0", 1024, minradius=1, maxradius=4,
                                atype_terms = ["AtmNum"],
                                btype_terms = []),
             "OpenEye-Circular/2 numbits=1024 minradius=1 maxradius=4 atype=AtmNum btype=0"),

            ("Circular,ver=2.0.0,size=512,radius=2-9,atype=None,btype=Chiral|InRing",
             CircularFPType("2.0.0", 512, minradius=2, maxradius=9,
                                atype_terms = [],
                                btype_terms = ["InRing", "Chiral"]),
             "OpenEye-Circular/2 numbits=512 minradius=2 maxradius=9 atype=0 btype=Chiral|InRing"),

             ]
        self._do_tests(test_cases)

    @unittest.skipUnless(has_oegraphsim, "OEGraphSim either not available or not licensed")
    def test_circular_enumeration(self):
        from openeye.oegraphsim import OEGetCircularFPType
        for numbits, minradius, maxradius in ((2**5, 0, 3), (2**6, 0, 0), (2**14, 3, 4), (2**15, 5, 10)):
            # 4, 4 is "atype=Chiral,btype=InRing"
            oe_type = OEGetCircularFPType(numbits, minradius, maxradius, 4, 4).GetFPTypeString()
            new_obj = fpbin.parse_oetype_string(oe_type)
            self.assertEqual(new_obj.size, numbits)
            self.assertEqual(new_obj.minradius, minradius)
            self.assertEqual(new_obj.maxradius, maxradius)

        def make_circular_atype(atype):
            return OEGetCircularFPType(1024, 0, 4, atype, 4)
        self._check_atypes(make_circular_atype)

        def make_circular_btype(btype):
            return OEGetCircularFPType(1024, 0, 4, 4, btype)
        self._check_btypes(make_circular_btype)
        
        
if __name__ == "__main__":
    unittest.main()
