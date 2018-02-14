class QueryBuilder(object):
    def __init__(self):
        self._type = None
        self._parent = None
        self._ancestor = None
        self._name_pattern = None
        self._last_modified_before = None
        self._last_modified_after = None
        self._page = None
        self._result_per_page = None

    def type(self, type):
        self._type = type
        return self

    def parent(self, parent):
        self._parent = parent
        return self

    def ancestor(self, ancestor):
        self._ancestor = ancestor
        return self

    def name_pattern(self, name_pattern):
        self._name_pattern = name_pattern
        return self

    def last_modified_before(self, last_modified_before):
        self._last_modified_before = last_modified_before
        return self

    def last_modified_after(self, last_modified_after):
        self._last_modified_after = last_modified_after
        return self

    def page(self, page):
        self._page = page
        return self

    def result_per_page(self, result_per_page):
        self._result_per_page = result_per_page
        return self

    def build(self):
        query_params = {"type": self._type, "parent": self._parent, "ancestor": self._ancestor, "namePattern": self._name_pattern,
                        "lastModifiedBefore": self._last_modified_before, "lastModifiedAfter": self._last_modified_after,
                        "page": self._page,
                        "resultsPerPage": self._result_per_page}
        return query_params
