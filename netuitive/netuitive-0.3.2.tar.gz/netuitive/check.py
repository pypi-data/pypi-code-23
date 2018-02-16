
class Check(object):

    """
        A Check model
        :param name: Check name
        :type name: string
        :param elementId: Associated Element ID
        :type elementId: string
        :param ttl: Check TTL in seconds
        :type ttl: int
    """

    def __init__(self,
                 name,
                 elementId,
                 ttl):

        self.name = name
        self.elementId = elementId
        self.ttl = ttl
