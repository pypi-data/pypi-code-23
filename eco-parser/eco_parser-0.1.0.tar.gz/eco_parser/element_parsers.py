import abc
from eco_parser.core import (
    DEFAULT_SCHEMA,
    get_single_element,
    get_elements_recursive,
    get_child_text,
    ParseError
)


class ElementParser(metaclass=abc.ABCMeta):

    def __init__(self, element):
        self.element = element

    @abc.abstractmethod
    def parse(self):
        pass


class TableParser(ElementParser):

    FORMAT_UNKNOWN        = 0
    FORMAT_STANDARD_TABLE = 1
    FORMAT_ONE_ROW_PARA   = 2

    def parse_head(self):
        thead = get_single_element(self.element, 'thead', schema='http://www.w3.org/1999/xhtml')
        headers = []
        for th in thead[0]:
            headers.append(get_child_text(th))
        return tuple(th for th in headers)

    def is_header(self, row):
        header_row = False
        for col in row:
            if col.tag == '{http://www.w3.org/1999/xhtml}th':
                header_row = True
        return header_row

    def get_table_format(self, tbody):
        if len(tbody) == 1:
            para_tags = tbody.xpath('//x:Para', namespaces={'x': DEFAULT_SCHEMA})
            if len(para_tags) > 0:
                return self.FORMAT_ONE_ROW_PARA
        elif len(tbody) > 1:
            return self.FORMAT_STANDARD_TABLE
        return self.FORMAT_UNKNOWN

    def parse_standard_table(self, tbody):
        data = []
        for row in tbody:
            if not self.is_header(row):
                data.append(tuple(get_child_text(col) for col in row))
        return data

    def parse_one_row_table(self, tbody):
        data = []
        tr = tbody[0]

        i = 0
        for td in tr:
            data.append([])
            for line in td:
                text = get_single_element(line, 'Text')
                data[i].append(get_child_text(text))
            i = i+1

        # check all the lists we've found are the same length
        # if not, throw an error
        len0 = len(data[0])
        for j in range(0, i):
            if len(data[j]) != len0:
                raise ParseError(
                    "Expected %i elements, found %i" % (len0, len(data[j])), 0)

        # transpose rows and columns
        return list(map(tuple, zip(*data)))

    def parse_body(self):
        tbody = get_single_element(self.element, 'tbody', schema='http://www.w3.org/1999/xhtml')
        table_format = self.get_table_format(tbody)
        if table_format == self.FORMAT_ONE_ROW_PARA:
            return self.parse_one_row_table(tbody)
        elif table_format == self.FORMAT_STANDARD_TABLE:
            return self.parse_standard_table(tbody)
        elif table_format == self.FORMAT_UNKNOWN:
            raise ParseError('Could not detect table format' ,0)

    def parse(self):
        try:
            header = [self.parse_head()]
        except ParseError:
            header = []
        return header + self.parse_body()


class BodyParser(ElementParser):

    def parse(self):
        elements = get_elements_recursive(self.element, 'Text')
        return [(get_child_text(el).strip().rstrip(',.;'),) for el in elements]


class ElementParserFactory:

    @staticmethod
    def create(element):
        try:
            tabular = get_single_element(element, 'Tabular')
            table = get_single_element(tabular, 'table', schema='http://www.w3.org/1999/xhtml')
            return TableParser(table)
        except ParseError as e:
            if e.matches == 0:
                return BodyParser(element)
            else:
                raise
