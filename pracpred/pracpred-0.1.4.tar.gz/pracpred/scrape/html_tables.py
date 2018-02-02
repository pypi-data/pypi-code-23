import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup


class HTMLTables():
    """One or more scraped HTML Tables from a URL."""

    def __init__(self, url, headers=None, table_class=None):
        self._url = url
        self._response = requests.get(
            url,
            allow_redirects=False,
            headers=headers,
            timeout=15,
        )
        self._response.raise_for_status()
        soup = BeautifulSoup(self._response.content, 'html.parser')
        if table_class:
            self._tables = soup.find_all('table', class_=table_class)
        else:
            self._tables = soup.find_all('table')

    def __getitem__(self, k):
        return self._tables[k]

    def __len__(self):
        return len(self._tables)

    def __iter__(self):
        return iter(self._tables)

    @property
    def shapes(self):
        """List of tuples of each table shape."""
        return [HTMLTables._table_dims(table) for table in self._tables]

    def unspan(self, soup=True, repeat_span=True):
        """Text or HTML from table, removing any rowspan or colspan structure."""
        unspanned = list()
        for table in self._tables:
            unspanned.append(HTMLTables._unspan_cells(table, soup=soup, repeat_span=repeat_span))
        return unspanned

    def to_dfs(self, repeat_span=True):
        """DataFrame of text from HTML table, removing any rowspan or colspan structure."""
        dfs = list()
        for table in self._tables:
            cells = HTMLTables._unspan_cells(table, repeat_span=repeat_span)
            n_rows, n_cols = cells.shape
            df = pd.DataFrame(
                index=range(n_rows),
                columns=range(n_cols),
                data=cells,
            )
            dfs.append(df)
        return dfs

    @staticmethod
    def _cols_in(row):
        return len(row.find_all(['td', 'th']))

    @staticmethod
    def _table_dims(table):
        n_rows = 0
        n_cols = 0
        for row in table.find_all('tr'):
            row_cols = HTMLTables._cols_in(row)
            if row_cols > 0:
                n_rows += 1
                # Find the max number of columns in any row
                n_cols = max(n_cols, row_cols)
        return n_rows, n_cols

    @staticmethod
    def _unspan_cells(table, soup=False, repeat_span=True):
        # Table dimension is rows x max number of columns in any row
        n_rows, n_cols = HTMLTables._table_dims(table)
        # Start with empty array of generic objects
        cells = np.empty((n_rows, n_cols), dtype=object)
        rows = table.find_all('tr')
        assert n_rows == len(rows)
        # Loop through rows
        rows_left_in_span = dict()
        for i, row in enumerate(rows):
            cols = row.find_all(['td', 'th'])
            col_index = 0 # where we are in the actual columns of this particular row
            cols_left_in_span = 0 # where we are within a colspan in this row
            for j in range(n_cols):
                # j is which column in the (initially empty) table we are currently at
                if j in rows_left_in_span:
                    # this table column is part of a rowspan
                    if repeat_span:
                        cells[i, j] = cells[i - 1, j] # get value from one row up
                    else:
                        cells[i, j] = np.nan # if don't want repeated values, just put NaN
                    # Reduce count of rows left in span; if done with this span, delete the span reference
                    rows_left_in_span[j] -= 1
                    if rows_left_in_span[j] == 0:
                        del rows_left_in_span[j]
                elif cols_left_in_span > 0:
                    # this table column is part of a colspan
                    if repeat_span:
                        cells[i, j] = cells[i, j - 1] # get value from one column to the left
                    else:
                        cells[i, j] = np.nan # if don't want repeated values, just put NaN
                    # Redue count of columns left in span
                    cols_left_in_span -= 1
                else:
                    # Don't know yet if this cell is stand-alone, or beginning of a new rowspan/colspan
                    # Get the actual cell from the soup object; remember col_index != j
                    col = cols[col_index]
                    # if we want raw soup, save that otherwise just get the cell text
                    cells[i, j] = col if soup else col.get_text()
                    col_index += 1
                    # Check if this is beginning of a new colspan
                    col_span = int(col['colspan']) if col.has_attr('colspan') else 0
                    if col_span > 0:
                        # Yes, so keep track of how many other table columns to use in span
                        cols_left_in_span = col_span - 1
                    # Check if this is the beginning of a new rowspan
                    row_span = int(col['rowspan']) if col.has_attr('rowspan') else 0
                    if row_span > 0:
                        # Yes, so keep track of how many other table rows to use in span
                        rows_left_in_span[j] = row_span - 1
        return cells
