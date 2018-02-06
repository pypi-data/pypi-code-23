from workfront.objects.codes import WFObjCode
from workfront.exceptions import WFException
from workfront.objects.generic_objects import WFParamValuesObject
import workfront.objects.task
import workfront.objects.program


def crt_from_template(wf, template_id, name):
    js = {
        "name": name,
        "templateID": template_id
    }
    data = wf.post_object(WFObjCode.project, js)
    return WFProject(wf, data["ID"])

def create_new(wf, params):
    data = wf.post_object(WFObjCode.project, params)
    return WFProject(wf, data["ID"])

class WFProject(WFParamValuesObject):

    def __init__(self, wf, idd):
        '''
        @param wf: A Workfront service object
        @param idd: worfront id of the project
        '''
        super(WFProject, self).__init__(wf, WFObjCode.project, idd)

    def get_template_id(self):
        '''
        @return: the template id of the project. None if it was not created
        from a template.
        '''
        r = self.wf.get_object(self.obj_code, self.wf_id, ["template:ID"])
        try:
            return r.json()["data"]["template"]["ID"]
        except Exception:
            return None

    def get_tasks(self):
        '''
        @return: A list of WFTask objects which belongs to this project
        '''
        r = self.wf.get_object(self.obj_code, self.wf_id, ["tasks:ID"])
        self._raise_if_not_ok(r)

        tasks = []
        for tdata in r.json()["data"]["tasks"]:
            t = workfront.objects.task.WFTask(self.wf, tdata["ID"])
            tasks.append(t)
        return tasks

    def get_program(self):
        r = self.wf.get_object(self.obj_code, self.wf_id, ["program:ID"])
        self._raise_if_not_ok(r)

        proj_id = r.json()["data"]["program"]["ID"]
        return workfront.objects.program.WFProgram(self.wf, proj_id)

    def set_status(self, status):
        '''
        :param idd: project id
        :param status: status code
        :return:
        '''
        r = self.wf.put_object(WFObjCode.project, self.wf_id, {"status": status})
        self._raise_if_not_ok(r)