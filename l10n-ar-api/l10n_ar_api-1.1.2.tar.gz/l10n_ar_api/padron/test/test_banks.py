import unittest
import sys
import random
sys.path.append("../")
import banks

class TestContribuyentes(unittest.TestCase):

    def setUp(self):
        self.banks_list = banks.Banks.get_banks_list()
        self.values = banks.Banks.get_values(self.banks_list)
        
    def test_check_values_types(self):
        
        values = []
        values.append(self.values[0])
        values.append(self.values[-1])
        values.append(random.choice(self.values))
        
        for bank in values:
            
            int(bank['cuit']) 
            int(bank['code'])
    
    def test_check_invalid_values_types(self):
        
        values = []
        values.append(self.values[0])
        values.append(self.values[-1])
        values.append(random.choice(self.values))
        
        for bank in values:
            
            int(bank['cuit']) 
            int(bank['code'])
            self.assertRaises(ValueError, lambda: int(bank['name']))

if __name__ == '__main__':
    unittest.main()