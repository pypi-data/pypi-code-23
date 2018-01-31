import datetime
import requests
import time

from crowdcurio_client.crowdcurio import (
    CrowdCurioAPIException, CrowdCurioObject
)

class Experiment(CrowdCurioObject):
    _api_slug = 'experiment'
    _link_slug = 'experiment'
    _edit_attributes = (
        'name',
        'group',
        'status',
        'params',
        'restrictions',
    )

    @classmethod
    def find(cls, id='', slug=None):
        if not id and not slug:
            return None
        return cls.where(id=id, slug=slug).next()

    def add(self, project, task):
        self.put(
            '{}'.format(self.id),
            json={"data": {"type": "Experiment", "id": self.id, "relationships": {"project":{ "data": { "type": "Project", "id": project.id}}, "task":{ "data": {"type": "Task", "id": task.id}} }}}
        )

    def remove(self, project, task):
        self.put(
            '{}'.format(self.id),
            json={"data": {"type": "Experiment", "id": self.id, "relationships": {"project":{}, "task":{} }}}
        )

    def destroy(self):
        self.delete('{}'.format(self.id), json={'data': {'type':'Experiment', 'id': self.id}})


class Condition(CrowdCurioObject):
    _api_slug = 'condition'
    _link_slug = 'condition'
    _edit_attributes = (
        'name',
        'configuration',
        'nb_subjects',
        'max_subjects',
        'status',
    )

    @classmethod
    def find(cls, id=''):
        if not id:
            return None
        return cls.where(id=id).next()

    def add(self, experiment):
        self.put(
            '{}'.format(self.id),
            json={"data": {"type": "Condition", "id": self.id, "relationships": {"experiment":{"data":{"type":"Experiment","id":experiment.id}}}}}
        )

    def remove(self, experiment):
        self.put(
            '{}'.format(self.id),
            json={"data": {"type": "Condition", "id": self.id, "relationships": {"experiment":{}}}}
        )

    def destroy(self):
        self.delete('{}'.format(self.id), json={'data': {'type':'Condition', 'id': self.id}})


class SubjectCondition(CrowdCurioObject):
    _api_slug = 'subjectcondition'
    _link_slug = 'subjectcondition'
    _edit_attributes = (
        'finished',
        'invalidated',
        'supplementary',
    )

    @classmethod
    def find(cls, id=''):
        if not id:
            return None
        return cls.where(id=id).next()

    def add(self, experiment, condition, user):
        self.put(
            '{}'.format(self.id),
            json={"data": {"type": "SubjectCondition", "id": self.id, "relationships": {"experiment":{"data":{"type":"Experiment","id":experiment.id}}, "condition":{"data":{"type":"Condition","id":condition.id}}, "user":{"data":{"type":"User","id":user.id}}}}}
        )

    def remove(self, experiment):
        self.put(
            '{}'.format(self.id),
            json={"data": {"type": "SubjectCondition", "id": self.id, "relationships": {"experiment":{}, "condition":{}, "user":{}}}}
        )

    def destroy(self):
        self.delete('{}'.format(self.id), json={'data': {'type':'SubjectCondition', 'id': self.id}})



class ConfirmationCode(CrowdCurioObject):
    _api_slug = 'experimentconfirmationcode'
    _link_slug = 'experimentconfirmationcode'
    _edit_attributes = (
        'code',
    )

    @classmethod
    def find(cls, id=''):
        if not id:
            return None
        return cls.where(id=id).next()

    def add(self, experiment, user):
        self.put(
            '{}'.format(self.id),
            json={"data": {"type": "ExperimentConfirmationCode", "id": self.id, "relationships": {"experiment":{"data":{"type":"Experiment","id":experiment.id}}, "user":{"data":{"type":"User","id":user.id}}}}}
        )

    def remove(self, experiment):
        self.put(
            '{}'.format(self.id),
            json={"data": {"type": "ExperimentConfirmationCode", "id": self.id, "relationships": {"experiment":{}, "user":{}}}}
        )

    def destroy(self):
        self.delete('{}'.format(self.id), json={'data': {'type':'ExperimentConfirmationCode', 'id': self.id}})


class BonusPayment(CrowdCurioObject):
    _api_slug = 'bonus'
    _link_slug = 'bonus'
    _edit_attributes = (
        'code',
    )

    @classmethod
    def find(cls, id=''):
        if not id:
            return None
        return cls.where(id=id).next()

    def destroy(self):
        self.delete('{}'.format(self.id), json={'data': {'type':'BonusPayment', 'id': self.id}})
