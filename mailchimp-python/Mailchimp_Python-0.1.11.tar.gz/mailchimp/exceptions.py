# coding=utf-8


class ObjectNotFound(Exception):
    message = "Object not found"


class MCListNotFound(Exception):
    def __init__(self, list_id, *args, **kwargs):
        super(MCListNotFound, self).__init__(*args, **kwargs)
        self.message = "List not found with id: %s" % list_id


class MCCategoryListNotFound(Exception):
    def __init__(self, list_id, category_id, *args, **kwargs):
        super(MCCategoryListNotFound, self).__init__(*args, **kwargs)
        self.message = "Category list not found with id: %s from list: %s" % (category_id, list_id)


class MCMemberNotFound(Exception):
    def __init__(self, list_id, member_id, *args, **kwargs):
        super(MCMemberNotFound, self).__init__(*args, **kwargs)
        self.message = "Unable to find member %s from list with id: %s" % (member_id, list_id)


class MCInterestCategoryNotFound(Exception):
    def __init__(self, list_id, category_id, *args, **kwargs):
        super(MCInterestCategoryNotFound, self).__init__(*args, **kwargs)
        self.message = "Unable to find interest category %s from list with id: %s" % (category_id, list_id)


class MCInterestNotFound(Exception):
    def __init__(self, list_id, category_id, interest_id, *args, **kwargs):
        super(MCInterestNotFound, self).__init__(*args, **kwargs)
        self.message = "Unable to find interest %s from category %s with list with id: %s" % (interest_id, category_id,
                                                                                              list_id)
