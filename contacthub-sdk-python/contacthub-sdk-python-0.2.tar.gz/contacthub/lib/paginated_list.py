from contacthub.errors.operation_not_permitted import OperationNotPermitted
from contacthub.lib.read_only_list import ReadOnlyList


class PaginatedList(ReadOnlyList):

    def __init__(self, node, function, entity_class, **kwargs):
        super(PaginatedList, self).__init__()
        self.node = node
        self.function = function
        self.entity_class = entity_class

        self.kwargs = kwargs
        self.page_number = 0
        self._retrieve_data()

    def next_page(self):
        """
        Retrieve the next page of entities in this PaginatedList

        :return: a PaginatedList containing the next page of entities compared to the current one
        """
        if self.page_number == self.total_pages - 1:
            raise OperationNotPermitted('Last page reached.')

        self.page_number += 1
        return self._retrieve_data()

    def previous_page(self):
        """
        Retrieve the previous page of entities in this PaginatedList

        :return: a PaginatedList containing the previous page of entities compared to the current one
        """
        if self.page_number == 0:
            raise OperationNotPermitted('First page reached.')

        self.page_number -= 1
        return self._retrieve_data()

    def _retrieve_data(self):
        self.kwargs['page'] = self.page_number
        resp = self.function(**self.kwargs)
        self.page = resp['page']
        self.size = self.page['size']
        self.total_elements = self.page['totalElements']
        self.total_pages = self.page['totalPages']
        self.total_unfiltered_elements = self.page['totalUnfilteredElements']
        self.page_number = self.page['number']

        list.__delitem__(self, slice(None, None, None))
        for element in resp['elements']:
            list.append(self, self.entity_class(node=self.node, **element))
        return self



