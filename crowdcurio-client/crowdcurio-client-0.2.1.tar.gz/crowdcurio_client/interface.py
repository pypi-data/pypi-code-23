from crowdcurio_client.crowdcurio import CrowdCurioObject

class Interface(CrowdCurioObject):
    """Help."""
    _api_slug = 'interface'
    _link_slug = 'interface'
    _edit_attributes = (
        'title',
        'repository',
        'commit',
    )

    @classmethod
    def find(cls, id='', slug=None):
        if not id and not slug:
            return None
        return cls.where(id=id, slug=slug).next()

    def add(self, task):
        """Adds a relationship between an Interface and a Task. (Performed via a PUT request.)"""
        self.put(
            '{}'.format(self.id),
            json={"data": {"type": "Task", "id": self.id, "relationships": {"task":{"data":{"type":"Task","id":task.id}}}}}
        )

    def remove(self, task):
        """Removes an existing relationship between an Interface and a Task. (Performed via a PUT request.)"""
        self.put(
            '{}'.format(self.id),
            json={"data": {"type": "Inteface", "id": self.id, "relationships": {"task":{}}}}
        )

    def destroy(self):
        """Deletes the Interface object."""
        self.delete('{}'.format(self.id), json={'data': {'type':'Interface', 'id': self.id}})