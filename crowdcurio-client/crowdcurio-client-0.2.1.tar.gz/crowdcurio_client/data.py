import datetime
import requests
import time

from crowdcurio_client.crowdcurio import CrowdCurioObject

class Data(CrowdCurioObject):
    _api_slug = 'data'
    _link_slug = 'data'
    _edit_attributes = (
        'slug',
        'name',
        'type',
        'url',
        'content',
        'order',
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
                json={"data": {"type": "Data", "id": self.id, "attributes": {"content": self.content},"relationships": {"task":{"data":{"type":"Task","id":task.id}} }}}
            )
        else:
            if condition == None:
                self.put(
                    '{}'.format(self.id),
                    json={"data": {"type": "Data", "id": self.id, "attributes": {"content": self.content},"relationships": {"task":{"data":{"type":"Task","id":task.id}}, "experiment":{"data":{"type":"Experiment","id":experiment.id}} }}}
                )
            else:
                self.put(
                    '{}'.format(self.id),
                    json={"data": {"type": "Data", "id": self.id, "attributes": {"content": self.content},"relationships": {"task":{"data":{"type":"Task","id":task.id}}, "experiment":{"data":{"type":"Experiment","id":experiment.id}}, "condition":{"data":{"type":"Condition","id":condition.id}} }}}
                )

    def remove(self, task, experiment):
        self.put(
            '{}'.format(self.id),
            json={"data": {"type": "Data", "id": self.id, "attributes": {"content": self.content}, "relationships": {"task":{}, "experiment": {}}}}
        )

    def destroy(self):
        self.delete('{}'.format(self.id), json={'data': {'type':'Data', 'id': self.id}})
