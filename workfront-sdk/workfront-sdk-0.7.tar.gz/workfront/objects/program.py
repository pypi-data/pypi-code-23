from workfront.objects.codes import WFObjCode
from workfront.exceptions import WFException
from workfront.objects.generic_objects import WFParamValuesObject
import workfront.objects.portfolio


def create_new(wf, params={}):
    '''
    :param params: dict of details for new project (must have: name, portfolioID)
    :return: Object of the new program
    '''
    r = wf.post_object("program", params)
    return WFProgram(wf, r["ID"])


class WFProgram(WFParamValuesObject):

    def __init__(self, wf, idd):
        '''
        @param wf: A Workfront service object
        @param idd: worfront id of the program
        '''
        super(WFProgram, self).__init__(wf, WFObjCode.program, idd)

    def get_portfolio(self):
        '''
        @return: the portfolio asociated with this program.
        '''
        r = self.wf.get_object(self.obj_code, self.wf_id, ["portfolio:ID"])
        self._raise_if_not_ok(r)

        proj_id = r.json()["data"]["portfolio"]["ID"]
        return workfront.objects.portfolio.WFPortfolio(self.wf, proj_id)

    def get_projects(self):
        '''
        @return: A list of WFProject objects which belongs to this program
        '''
        r = self.wf.get_object(self.obj_code, self.wf_id, ["projects:ID"])
        self._raise_if_not_ok(r)

        projects = []
        for pdata in r.json()["data"]["projects"]:
            t = workfront.objects.project.WFProject(self.wf, pdata["ID"])
            projects.append(t)
        return projects
