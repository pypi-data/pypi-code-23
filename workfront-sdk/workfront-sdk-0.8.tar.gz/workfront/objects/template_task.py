from workfront.objects.codes import WFObjCode
from workfront.objects.generic_objects import WFParamValuesObject


class WFTemplateTask(WFParamValuesObject):

    def __init__(self, wf, idd):
        '''
        @param wf: A Workfront service object
        @param idd: worfront id of a template task
        '''
        super(WFTemplateTask, self).__init__(wf, WFObjCode.templat_task, idd)
