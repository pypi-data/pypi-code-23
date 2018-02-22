# -*- coding: utf-8 -*-


class ReadOnlyList(list):
    """
    Read only list for managing list in the entities.
    This class blocks some possible operations on a regular list
    """

    @staticmethod
    def not_implemented(*args, **kwargs):
        """
        Raise a new ValueError for blocking forbidden operations.
        """
        raise ValueError("Read Only list proxy")

    remove = reverse = append = pop = extend = insert = __setitem__ = __setslice__ = __delitem__ = not_implemented
