import unittest
import ucsc_db

class TestParseSample(unittest.TestCase):

    ucsc = ucsc_db.connect_ucsc()

    def test_db_version(self):
        self.assertEqual(self.ucsc.db, 'hg19')

    def test_nm(self):

        nm_list = ['NM_005450']
        regions = self.ucsc.queryStructureByNm(nm_list, True)

        self.assertEqual(regions, [['17', '54671584', '54672283', 'NOG', 'NM_005450']])

if __name__ == "__main__":
    unittest.main()
