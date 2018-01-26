# -*- coding: utf-8 -*-

### imports ###################################################################
import unittest

### local imports #############################################################
import qvpy

### local imports from ########################################################
from qvpy import qvpak

###############################################################################
class TestStringMethods(unittest.TestCase):

    mitutoyo = qvpak.Mitutoyo()


    def test_00_package(self):
        version = qvpy.__version__
        project = qvpy.__project__
        
        self.assertRegex(version, '[0-9].[0-9].[0-9]')
        self.assertRegex(project, '[a-zA-Z0-9_]')


    def test_01_init(self):
        TestStringMethods.mitutoyo.init()

    
    def test_02_info(self):
        TestStringMethods.mitutoyo.info()


    def test_03_pcs_import(self):
        result = TestStringMethods.mitutoyo.pcs_import('data/Waferrahmen.pcs')
        self.assertGreater(result, 0)


    def test_99_cleanUp(self):
        result = TestStringMethods.mitutoyo.cleanUp()
        self.assertGreater(result, 0)
    
    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)
