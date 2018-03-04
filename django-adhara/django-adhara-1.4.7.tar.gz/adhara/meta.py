from .exceptions import InvalidInput


class Page:

    def __init__(self, start=None, length=None, page=None):
        if page:
            try:
                start = page["start"]
            except KeyError:
                pass
            try:
                length = page["length"]
            except KeyError:
                pass
        if start is not None and start < 1:
            raise InvalidInput("Start index cannot be less than 1")
        if length and length > 50:
            length = 50
        self._start = start or 1
        self._length = length or 10

    def get_start(self):
        return self._start

    def get_length(self):
        return self._length

    def get_end(self):
        return self._start + self.get_length() - 1

    def to_dict(self):
        return {
            "start": self.get_start(),
            "length": self.get_length()
        }


class Pagination:

    def __init__(self, current_page=None):
        if current_page:
            self._current_page = current_page
        else:
            self._current_page = Page()
        self._updated_current_page = None
        self._total_count = 0

    def get_current_page(self):
        return self._current_page

    def set_current_page(self, page):
        self._current_page = page

    def update_page_properties(self, current_page_count, total_count):
        self._updated_current_page = Page(self.get_current_page().get_start(), current_page_count)
        self._total_count = total_count

    def get_next_page(self):
        curr_end = self.get_current_page().get_end()
        curr_len = self.get_current_page().get_length()
        if curr_end < self._total_count:
            next_total = self._total_count - curr_end
            next_len = next_total if next_total < curr_len else curr_len
            return Page(curr_end+1, next_len)
        return None

    def get_previous_page(self):
        curr_start = self.get_current_page().get_start()
        if curr_start > 1:
            curr_len = self.get_current_page().get_length()
            # prev_len = curr_start if curr_start < curr_len else curr_len
            prev_len = curr_len
            prev_start = curr_start - prev_len
            if prev_start < 1:
                prev_start = 1
            return Page(prev_start, prev_len)
        return None

    def to_dict(self):
        next_page = self.get_next_page()
        if next_page:
            next_page = next_page.to_dict()
        previous_page = self.get_previous_page()
        if previous_page:
            previous_page = previous_page.to_dict()
        return {
            "previous": previous_page,
            "current": self.get_current_page().to_dict(),
            "next": next_page
        }


class Meta:

    def __init__(self, current_page=None, order_by=None, required_fields=None):
        self._pagination = Pagination(current_page)
        self._order_by = order_by
        self._required_fields = required_fields
        self._total_count = None

    def get_pagination(self):
        return self._pagination

    def get_order_by(self):
        return self._order_by

    def set_order_by(self, *order_by):
        self._order_by = order_by

    def set_required_fields(self, *fields):
        self._required_fields = fields

    def get_required_fields(self):
        if self._required_fields:
            required_fields = list(self._required_fields)
            required_fields.append("id")
            return required_fields
        else:
            return ()

    def update_page_properties(self, current_page_count, total_count):
        self._total_count = total_count
        self._pagination.update_page_properties(current_page_count, total_count)

    def to_dict(self):
        return {
            "page": self.get_pagination().to_dict(),
            "total_count": self._total_count
        }
