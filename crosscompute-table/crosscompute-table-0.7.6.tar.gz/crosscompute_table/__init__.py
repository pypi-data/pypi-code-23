import pandas as pd
from invisibleroads_macros.disk import get_file_extension
from invisibleroads_macros.table import load_csv_safely
from crosscompute.exceptions import DataTypeError
from crosscompute.scripts.serve import import_upload_from
from crosscompute.types import DataType
from io import StringIO
from os.path import exists

from .exceptions import EmptyTableError


class TableType(DataType):
    suffixes = 'table',
    formats = 'csv', 'json'
    style = 'crosscompute_table:assets/part.min.css'
    script = 'crosscompute_table:assets/part.min.js'
    template = 'crosscompute_table:type.jinja2'
    views = [
        'import_table',
    ]
    requires_value_for_path = False

    @classmethod
    def save(Class, path, table):
        if path.endswith('.csv'):
            table.to_csv(path, encoding='utf-8', index=False)
        elif path.endswith('.csv.xz'):
            table.to_csv(path, encoding='utf-8', index=False, compression='xz')
        elif path.endswith('.msg'):
            table.to_msgpack(path, compress='blosc')
        elif path.endswith('.json'):
            table.to_json(path)
        elif path.endswith('.xls') or path.endswith('.xlsx'):
            table.to_excel(path)
        else:
            raise DataTypeError(
                'file format not supported (%s)' % get_file_extension(path))

    @classmethod
    def load(Class, path, default_value=None):
        if not exists(path):
            raise IOError('file not found (%s)' % path)
        try:
            if (
                    path.endswith('.csv') or
                    path.endswith('.csv.gz') or
                    path.endswith('.csv.tar.gz') or
                    path.endswith('.csv.tar.xz') or
                    path.endswith('.csv.xz') or
                    path.endswith('.csv.zip')):
                table = load_csv_safely(path)
            elif path.endswith('.msg'):
                table = pd.read_msgpack(path)
            elif path.endswith('.json'):
                table = pd.read_json(path, orient='split')
            elif path.endswith('.xls') or path.endswith('.xlsx'):
                table = pd.read_excel(path)
            else:
                raise DataTypeError((
                    'file format not supported '
                    '(%s)' % get_file_extension(path)))
        except pd.errors.EmptyDataError:
            raise EmptyTableError('file empty')
        return table

    @classmethod
    def parse(Class, x, default_value=None):
        if isinstance(x, pd.DataFrame):
            return x
        return load_csv_safely(StringIO(x))

    @classmethod
    def render(Class, table, format_name='csv'):
        if format_name == 'csv':
            return table.to_csv(encoding='utf-8', index=False)
        elif format_name == 'json':
            return table.to_json(orient='split')


def import_table(request):
    return import_upload_from(request, TableType, {'class': 'editable'})
