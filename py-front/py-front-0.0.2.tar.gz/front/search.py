from itertools import tee

from front.api import client


class ListSet:
    _pagination_key = '_pagination'
    _next_key = 'next'
    _results_key = '_results'

    def __init__(self, resource_cls, response=None):
        self._resource_cls = resource_cls
        self._response = response or client.get(
            self._resource_cls.Meta.list_path
        )
        self._results = self._results_generator()

    def __iter__(self):
        self._results, cpy = tee(self._results)
        return cpy

    def __call__(self, *args, **kwargs):
        return self

    def all(self):
        return self

    def _results_generator(self):
        if self._pagination_key in self._response:
            yield from self._paginate()
        else:
            yield from self._build_resources(self._response[self._results_key])

    def _paginate(self):
        next_page = self._response[self._pagination_key].get(self._next_key)
        if next_page is None:
            yield from self._build_resources(self._response[self._results_key])
        else:
            while next_page is not None:
                yield from self._build_resources(
                    rows=self._response[self._results_key]
                )

                self._response = client.get(next_page, raw_url=True)
                pagination_data = self._response[self._pagination_key]
                next_page = pagination_data.get(self._next_key)

    def _build_resources(self, rows):
        for row in rows:
            yield self._resource_cls.from_api_data(row)
