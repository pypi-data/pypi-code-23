from workfront.objects.codes import WFObjCode
from workfront.objects.generic_objects import WFParamValuesObject


class WFPortfolio(WFParamValuesObject):

    def __init__(self, wf, idd):
        '''
        @param wf: A Workfront service object
        @param idd: worfront id of the portfolio
        '''
        super(WFPortfolio, self).__init__(wf, WFObjCode.portfolio, idd)
