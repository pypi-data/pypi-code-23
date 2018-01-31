from crowdcurio_client.crowdcurio import CrowdCurioObject

class Event(CrowdCurioObject):
    """Help."""
    _api_slug = 'event'
    _link_slug = 'event'
    _edit_attributes = (
        'session',
        'content',
    )

    @classmethod
    def find(cls, id='', slug=None):
        if not id and not slug:
            return None
        return cls.where(id=id, slug=slug).next()