# -*- coding: utf-8 -*-

### imports ###################################################################
import unittest

### local imports #############################################################
import qvpy

### local imports from ########################################################
from qvpy import qvpak


###############################################################################
class TestMitutoyo(unittest.TestCase):

    mitutoyo = qvpak.Mitutoyo()

    def test_00_package(self):
        version = qvpy.__version__
        project = qvpy.__project__

        self.assertRegex(version, '[0-9].[0-9].[0-9]')
        self.assertRegex(project, '[a-zA-Z0-9_]')

    def test_01_init(self):
        TestMitutoyo.mitutoyo.init()

    def test_02_info(self):
        TestMitutoyo.mitutoyo.info()

    def test_03_pcs_import(self):
        result = TestMitutoyo.mitutoyo.pcs_import('data/Waferrahmen.pcs')
        self.assertGreater(result, 0)

    def test_99_cleanUp(self):
        result = TestMitutoyo.mitutoyo.cleanUp()
        self.assertGreater(result, 0)
