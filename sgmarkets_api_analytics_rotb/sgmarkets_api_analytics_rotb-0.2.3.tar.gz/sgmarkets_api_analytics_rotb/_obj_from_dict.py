
class ObjFromDict:
    """
    Returns object with same structure as dict
    """

    def __init__(self, dic):
        """
        """
        for k, v in dic.items():
            if isinstance(v, dict):
                self.__dict__[k] = ObjFromDict(v)
            else:
                self.__dict__[k] = v

    def __repr__(self):
        return str(self.__dict__)

    def __copy__(self):
        return ObjFromDict(self.__dict__)
