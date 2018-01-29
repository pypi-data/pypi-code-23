from __future__ import print_function
from gns_1 import GNS
from gns_api import GNS_api
import numpy as np
import os
import unittest



class TestGNS(unittest.TestCase):

    def setUp(self):
        self.gns_1 = GNS()
        self.gns_api = GNS_api()
        #pass
    
        
    def test_generate_image_sequence_test(self):
        img=self.gns_1.generate_numbers_sequence([1,2],(0,20),66)
        rows, cols = img.shape
        self.assertEqual(rows, 28)
        self.assertEqual(cols, 66)
        self.assertEqual(np.amax(img), 1.0) 
        self.assertEqual(np.amin(img),0.0)
      
    def test_save_image_test(self):
        img=(self.gns_1.generate_numbers_sequence([1,2],(0,20),66)*255).astype(np.uint8)
        self.gns_api.save_img((img), [1, 2])
        self.assertTrue(os.path.isfile("0-1.png"))

    


if __name__ == '__main__':
    unittest.main()