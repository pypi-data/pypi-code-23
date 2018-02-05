# -*- coding: utf-8 -*-
# * Authors:
#       * Arezki Feth <f.a@majerti.fr>;
#       * Miotte Julien <j.m@majerti.fr>;
#       * TJEBBES Gaston <g.t@majerti.fr>
"""
    Csv exporter for sqlalchemy datas

    uses the sqlalchemy info attr to retrieve meta datas about the columns
"""
from __future__ import absolute_import
import csv
import cStringIO as StringIO

from sqla_inspect.ascii import force_encoding
from sqla_inspect.export import (
    BaseExporter,
    SqlaExporter,
)


CSV_DELIMITER = ';'
CSV_QUOTECHAR = '"'


class CsvWriter(object):
    """
    A base csv writer

    headers are stored in the form of dicts
    {'label': "Header", "name": "header"}

    rows are also stored as dicts in the form {'header': 'value}
    """
    delimiter = CSV_DELIMITER
    quotechar = CSV_QUOTECHAR
    default_encoding = 'utf-8'

    def __init__(self, **kw):
        if 'encoding' in kw:
            self.encoding = kw['encoding']
        else:
            self.encoding = self.default_encoding

        self.options = kw

    def render(self, f_buf=None):
        """
        Write to the dest buffer

        :param obj f_buf: A file buffer supporting the write and seek
        methods
        """
        if f_buf is None:
            f_buf = StringIO.StringIO()

        headers = getattr(self, 'headers', ())

        keys = [
            force_encoding(header['label'], self.encoding)
            for header in headers
        ]

        extra_headers = getattr(self, 'extra_headers', ())
        keys.extend([
            force_encoding(header['label'], self.encoding)
            for header in extra_headers
        ])

        outfile = csv.DictWriter(
            f_buf,
            keys,
            extrasaction='ignore',
            delimiter=self.delimiter,
            quotechar=self.quotechar,
            quoting=csv.QUOTE_ALL,
        )
        outfile.writeheader()
        _datas = getattr(self, '_datas', ())
        outfile.writerows(_datas)
        f_buf.seek(0)
        return f_buf

    def format_row(self, row):
        """
        Format the row to fit our export switch the key used to store it in the
        dict

        since csv writer is expecting dict with keys matching the headers' names
        we switch the name the attributes fo the row are stored using labels
        instead of names
        """
        res_dict = {}
        headers = getattr(self, 'headers', [])
        extra_headers = getattr(self, 'extra_headers', [])
        for header in tuple(headers) + tuple(extra_headers):
            name, label = header['name'], header['label']
            val = row.get(name)
            if val is None:
                continue
            label = force_encoding(label, self.encoding)
            if hasattr(self, "format_%s" % name):
                val = getattr(self, "format_%s" % name)(val)

            res_dict[label] = force_encoding(val, self.encoding)
        return res_dict

    def set_headers(self, headers):
        """
        Set the headers of our csv writer

        :param list headers: list of dict with label and name key (label is
        mandatory : used for the export)
        """
        self.headers = []
        if 'order' in self.options:
            for element in self.options['order']:
                for header in headers:
                    if header['key'] == element:
                        self.headers.append(header)
                        break
        else:
            self.headers = headers


class SqlaCsvExporter(CsvWriter, SqlaExporter):
    """
    Main class used for exporting a SQLAlchemy model to a csv format

    Models attributes output can be customized through the info param :

        Column(Integer, infos={'export':
            {
            'csv': <csv specific options>,
            <main_export_options>
            }
        })

    main_export_options and csv_specific_options can be :

        label

            label of the column header

        format

            a function that will be fired on each row to format the output

        related_key

            If the attribute is a relationship, the value of the given attribute
            of the related object will be used to fill the cells

        exclude

            This data will not be inserted in the export if True

        encoding

            The encoding of the csv output

    Usage:

        a = SqlaCsvWriter(MyModel, encoding='utf-8')
        for i in MyModel.query().filter(<myfilter>):
            a.add_row(i)
        a.render()

        You get a file buffer with the csv formatted datas

    """
    config_key = 'csv'

    def __init__(self, model, **kw):
        CsvWriter.__init__(self, **kw)
        SqlaExporter.__init__(self, model, **kw)

    def add_extra_datas(self, extra_datas):
        """
        Add extra datas to the last row
        headers : [col1, col2, col3, col4, col5]
        row : {col1: a1, col2: a2, col3: a3}
        extra_datas : [a4, a5]

        row becomes : {col1: a1, col2: a2, col3: a3, col4: a4, col5: a5}

        in case of longer extra_datas, the last columns will be overriden

        :param list extra_datas: list of values to set in the last columns
        """
        # we will add datas starting from the last index
        for index, data in enumerate(extra_datas):
            header = self.extra_headers[index]
            self._datas[-1][header['label']] = data


class CsvExporter(CsvWriter, BaseExporter):
    """
    A common csv writer to be subclassed
    Set a header attribute and use it

    class MyCsvExporter(CsvExporter):
        headers = ({'name': 'key', 'label': u'Ma colonne 1'}, ...)

    writer = MyCsvExporter(encoding='utf-8')
    writer.add_row({'key': u'La valeur de la cellule de la colonne 1'})
    writer.render()
    """
    headers = ()

    def __init__(self, **kw):
        CsvWriter.__init__(self, **kw)
        BaseExporter.__init__(self, **kw)

    def add_extra_datas(self, extra_datas):
        """
        Add extra datas to the last row
        headers : [col1, col2, col3, col4, col5]
        row : {col1: a1, col2: a2, col3: a3}
        extra_datas : [a4, a5]

        row becomes : {col1: a1, col2: a2, col3: a3, col4: a4, col5: a5}

        in case of longer extra_datas, the last columns will be overriden

        :param list extra_datas: list of values to set in the last columns
        """
        # we will add datas starting from the last index
        for index, data in enumerate(extra_datas):
            header = self.extra_headers[index]
            self._datas[-1][header['label']] = data


def get_csv_reader(csv_buffer, delimiter=CSV_DELIMITER,
                   quotechar=CSV_QUOTECHAR):
    return csv.DictReader(
        csv_buffer,
        delimiter=delimiter,
        quotechar=quotechar,
    )
