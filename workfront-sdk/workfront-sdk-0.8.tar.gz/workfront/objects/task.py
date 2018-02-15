from workfront.exceptions import WFException
from workfront.objects.codes import WFObjCode
from workfront.objects import user
from workfront.objects.generic_objects import WFParamValuesObject
import workfront.objects.project
import workfront.objects.template_task


class WFTask(WFParamValuesObject):
    '''
    @summary: A Workfront Task helper class
    '''

    def __init__(self, wf, idd):
        '''
        @param wf: A Workfront service object
        @param idd: worfront id of the task
        '''
        super(WFTask, self).__init__(wf, WFObjCode.task, idd)

    def set_status(self, status):
        '''
        @summary: Hit WF to set the status of the current task.
        @param status: one of the WFTaskStatus
        '''
        r = self.wf.put_object(WFObjCode.task, self.wf_id, {"status": status})
        self._raise_if_not_ok(r)

    def get_status(self):
        '''
        @return: the status of the current task ( can be one of the
        WFTaskStatus)
        '''
        r = self.wf.get_object(WFObjCode.task, self.wf_id, ["status"])
        return r.json()["data"]["status"]

    def assign_to_user(self, user):
        '''
        @summary: Assign the current task to the given user.
        @param user: an instance of WFUser
        '''
        params = {
            "objID": user.wf_id,
            "objCode": WFObjCode.user
        }
        r = self.wf.action(WFObjCode.task, self.wf_id, "assign", params)
        self._raise_if_not_ok(r)

    def unassign_from_user(self, user):
        params = {
            "userID": user.wf_id,
        }
        r = self.wf.action(WFObjCode.task, self.wf_id, "unassign", params)
        self._raise_if_not_ok(r)

    def get_assigned_user(self):
        '''
        @return: an instance of the user (WFUser object) that is assigned to
        the current task.
        '''
        r = self.get_fields(["assignedTo:*"])

        u = user.WFUser(self.wf, js=r["assignedTo"])
        return u

    def get_project(self):
        r = self.wf.get_object(WFObjCode.task, self.wf_id, ["project:ID"])
        self._raise_if_not_ok(r)

        proj_id = r.json()["data"]["project"]["ID"]
        return workfront.objects.project.WFProject(self.wf, proj_id)

    def get_successors(self):
        r = self.wf.get_object(WFObjCode.task, self.wf_id, ["successors:*"])
        self._raise_if_not_ok(r)

        successors = r.json()["data"]["successors"]
        return[s['successorID'] for s in successors]

    def get_handoff_date(self):
        r = self.wf.get_object(WFObjCode.task, self.wf_id, ["handoffDate"])
        self._raise_if_not_ok(r)

        return r.json()["data"]["handoffDate"]

    def get_template(self):
        '''
        @return: an instance of template task from where this task was created.
        '''
        ttaskid = self.get_fields(["templateTask:ID"])["templateTask"]["ID"]
        return workfront.objects.template_task.WFTemplateTask(self.wf, ttaskid)
