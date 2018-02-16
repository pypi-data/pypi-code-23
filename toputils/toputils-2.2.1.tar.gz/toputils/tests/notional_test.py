from scipy.stats import logistic

from toputils.notional_line import finder

def test_no_change():
    assert finder(6.5, 0.5, logistic, scale=21) == 6.5
    

def test_notional_smaller():
    assert finder(6.5, 0.6, logistic, scale=15) < 6.5
    
    
def test_notional_bigger():
    assert finder(-6.5, 0.45, logistic, scale=6.5) > -6.5
