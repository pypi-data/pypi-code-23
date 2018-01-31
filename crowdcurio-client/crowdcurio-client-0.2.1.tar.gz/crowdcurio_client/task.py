import datetime
import requests
import time

from crowdcurio_client.crowdcurio import (
    CrowdCurioAPIException, CrowdCurioObject
)

class Task(CrowdCurioObject):
    _api_slug = 'task'
    _link_slug = 'task'
    _edit_attributes = (
        'slug',
        'name',
        'motivation',
        'question',
        'avatar',
        'configuration',
    )

    @classmethod
    def find(cls, id='', slug=None):
        if not id and not slug:
            return None
        return cls.where(id=id, slug=slug).next()

    def add(self, project, interface):
        """Creates a relationship between a Project and a Task."""
        self.put(
            '{}'.format(self.id),
            json={"data": {"type": "Task", "id": self.id, "relationships": {"project":{"data":{"type":"Project","id":project.id}}, "interface": {"data":{"type":"Interface","id":interface.id}}}}}
        )

    def remove(self):
        """Removes a Task's existing relationships to Projects."""
        self.put(
            '{}'.format(self.id),
            json={"data": {"type": "Task", "id": self.id, "relationships": {"project":{}, "interface":{}}}}
        )

    def destroy(self):
        """Deletes the Task object."""
        self.delete('{}'.format(self.id), json={'data': {'type':'Task', 'id': self.id}})


class TaskSessionPolicy(CrowdCurioObject):
    """Class for managing TaskSessionPolicy instances."""
    _api_slug = 'tasksessionpolicy'
    _link_slug = 'tasksessionpolicy'
    _edit_attributes = (
        'configuration',
        {}
    )

    @classmethod
    def find(cls, id='', slug=None):
        if not id and not slug:
            return None
        return cls.where(id=id, slug=slug).next()

    def add(self, task, experiment = None, condition = None):
        if experiment == None and condition == None:
            self.put(
                '{}'.format(self.id),
                json={"data": {"type": "TaskSessionPolicy", "id": self.id, "attributes": {"configuration": self.configuration},"relationships": {"task":{"data":{"type":"Task","id":task.id}} }}}
            )
        else:
            if condition == None:
                self.put(
                    '{}'.format(self.id),
                    json={"data": {"type": "TaskSessionPolicy", "id": self.id, "attributes": {"configuration": self.configuration},"relationships": {"task":{"data":{"type":"Task","id":task.id}}, "experiment":{"data":{"type":"Experiment","id":experiment.id}} }}}
                )
            else:
                self.put(
                    '{}'.format(self.id),
                    json={"data": {"type": "TaskSessionPolicy", "id": self.id, "attributes": {"configuration": self.configuration},"relationships": {"task":{"data":{"type":"Task","id":task.id}}, "experiment":{"data":{"type":"Experiment","id":experiment.id}}, "condition":{"data":{"type":"Condition","id":condition.id}} }}}
                )

    def remove(self, task, experiment):
        self.put(
            '{}'.format(self.id),
            json={"data": {"type": "TaskSessionPolicy", "id": self.id, "attributes": {"configuration": self.configuration}, "relationships": {"task":{}, "experiment": {}}}}
        )

    def destroy(self):
        self.delete('{}'.format(self.id), json={'data': {'type':'TaskSessionPolicy', 'id': self.id}})
