import pytest
import sys, os
sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/.."))
from contributor import Contributor

class TestContribuyentes():

    def test_valid_cuit(self):    
        cuit = '30709653543'
        assert Contributor.is_valid_cuit(cuit) 
        cuit = 30709653543
        assert Contributor.is_valid_cuit(cuit)

    def test_invalid_cuit(self):
        cuit = '30709653542'
        assert Contributor.is_valid_cuit(cuit) == 0
        cuit = 30709653542
        assert Contributor.is_valid_cuit(cuit) == 0

    def test_cuit_without_11_digits(self):
        cuit = '3070965354'
        assert Contributor.is_valid_cuit(cuit) == 0
        cuit = 3070965354
        assert Contributor.is_valid_cuit(cuit) == 0
                        
    def test_11_digits_no_int(self):  
        cuit = 'A1234567891'
        assert Contributor.is_valid_cuit(cuit) == 0
        
    def test_cuit_with_dash(self):
        cuit = '30-70965354-3'
        assert Contributor.is_valid_cuit(cuit) == 0
    
    def test_get_partner_data(self):
        Contributor.get_partner_data('30709653543')
        
    def test_get_data_invalid_url(self):
        with pytest.raises(ValueError):
            Contributor.get_partner_data('30709653543', url="invalidUrl")
                
    def test_get_data_no_json(self):
        with pytest.raises(ValueError):
            Contributor.get_partner_data('30709653543', url="https://www.google.com.ar/?gfe_rd=cr&ei=uWRqWLaUNYyTwASCjLPABQ&gws_rd=ssl#q=")
        
    def test_set_partner_data(self):
        contributor = Contributor()
        contributor.set_partner_data('30712097953')
        assert contributor.document_number == '30712097953'
        assert contributor.name == 'OPENPYME SRL'
        assert contributor.postal_code == '1425'
        assert contributor.street == 'BILLINGHURST 1964'
        assert contributor.state_code == 0

    def test_set_partner_data_invalid_cuit(self):
        contributor = Contributor()
        contributor.set_partner_data('307120979531')
        assert contributor.document_number == '307120979531'
        assert contributor.name == None
        assert contributor.postal_code == None
        assert contributor.street == None
        assert contributor.state_code == None