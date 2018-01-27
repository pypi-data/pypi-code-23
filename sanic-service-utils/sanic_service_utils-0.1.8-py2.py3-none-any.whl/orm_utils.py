from typing import Dict, Any

from anji_orm.model import Model
import rethinkdb as R
from sanic.request import Request
from sanic.response import json

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.1.8"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = ['DataTableMixin']


SEARCH_TARGET_FIELD_MARK = 'search_target'


class DataTableMixin(Model):

    async def convert_to_web_info(self) -> Dict[str, Any]:
        fields = {}
        for field_name, field_item in self._fields.items():
            if field_item.displayed and getattr(self, field_name) is not None:
                fields[field_item.name] = await field_item.async_format(getattr(self, field_name))
        return fields

    @classmethod
    def process_after_filter(cls, db_request: R.RqlQuery, _request: Request) -> R.RqlQuery:
        return db_request

    @classmethod
    def process_filter(cls, db_request: R.RqlQuery, primary_key: str, request: Request) -> R.RqlQuery:
        return db_request.filter(lambda doc: doc[primary_key].match(request.args.get('filter')))

    @classmethod
    def process_sort(cls, db_request: R.RqlQuery, request: Request) -> R.RqlQuery:
        column_link = request.args.get('sortColumn')
        if request.args.get('sortDirection') == 'desc':
            column_link = R.desc(column_link)
        return db_request.order_by(column_link)

    @classmethod
    def process_pager(cls, db_request: R.RqlQuery, request: Request) -> R.RqlQuery:
        page_index = int(request.args.get('pageIndex'))
        page_size = int(request.args.get('pageSize'))
        return db_request.skip(page_index * page_size).limit(page_size)

    @classmethod
    async def process_web_request(cls, request: Request, primary_key: str = None) -> Dict[str, Any]:
        if not primary_key:
            primary_key = next(iter(cls._primary_keys), primary_key)
        db_request: R.RqlQuery = cls.all()
        if 'filter' in request.args and primary_key is not None:
            db_request = cls.process_filter(db_request, primary_key, request)
        db_request = cls.process_after_filter(db_request, request)
        total_count = await cls.async_execute(db_request.count())
        if 'sortColumn' in request.args:
            db_request = cls.process_sort(db_request, request)
        if 'pageIndex' in request.args and 'pageSize' in request.args:
            db_request = cls.process_pager(db_request, request)
        records = await cls.async_execute(db_request)
        return json(
            {
                'data': [await record.convert_to_web_info() for record in records],
                'total': total_count
            }
        )
