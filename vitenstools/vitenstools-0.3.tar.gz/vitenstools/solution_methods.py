from phreeqpython import Solution
from .cijfer import cijfer
from .grenswaarden import grenswaarden

#######################################
# Vitens specific solution extensions #
#######################################

def si90(self, phase):

    tmp = self.copy()
    tmp.change_temperature(90)

    si = tmp.si(phase)

    tmp.forget()
    return si

def tacc(self,temperature=None):
    """ Calculate the Calcium Carbonate Precipitation Potential (CCPP)"""
    # create temporary solution
    tmp = self.copy()
    # raise temperature
    if temperature and temperature is not self.temperature:
        tmp.change_temperature(temperature)
    ca_pre = tmp.total_element('Ca')
    # use saturate instead of desaturate to allow dissolution in addition to precipitation
    tmp.equalize('Calcite',0.0)
    # calculate tacc
    tacc = ca_pre - tmp.total_element('Ca')
    # cleanup
    self.pp.remove_solutions([tmp.number])
    return tacc #mmol

@property
def aggco2(self):
    tacc = self.tacc(self.temperature)
    if tacc < 0:
        return abs(tacc)
    else:
        return 0

def score(self,test, precision=2):
    """ Returns the score for a Vitens grens- en drempelwaarden test """
    test_values = grenswaarden[test]
    # perform lambda function
    value = test_values[5](self)
    return round(cijfer(value,test_values[2],test_values[1],test_values[3],test_values[4]),precision)

@property
def scores(self):
    scores = {}
    for test in grenswaarden.keys():
        scores[test] = score(self,test)
    return scores

# vitens TACC90 calculation
@property
def tacc90(self):
    return self.tacc(90)

@property
def th(self):
    return (self.total_element('Ca')+self.total_element('Mg'))*1e3

# Vitens EGV calculation at 20 degrees
@property
def egv(self):
    tmp = self.copy()
    tmp.change_temperature(20)
    egv = tmp.sc
    tmp.forget()
    return egv

@property
def egv25(self):
    tmp = self.copy()
    tmp.change_temperature(25)
    egv = tmp.sc
    tmp.forget()
    return egv

# extend class
Solution.tacc = tacc
Solution.tacc90 = tacc90
Solution.aggco2 = aggco2
Solution.score = score
Solution.scores = scores
Solution.egv = egv
Solution.egv25 = egv25
Solution.si90 = si90
Solution.th = th
