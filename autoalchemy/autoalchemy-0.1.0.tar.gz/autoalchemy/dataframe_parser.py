"""
A class providing an interface to extract metadata and infer the schema
and dtypes of pandas DataFrames.
"""
import os

import pandas as pd
from autoalchemy.utils import (get_filename, make_valid_name,
                               remove_numeric_head, validate_path)
from pandas.api.types import is_datetime64_any_dtype


def enforce_pass_by_reference(func):
    """Decorator to add checking that a dataframe is being modified in place. Consumes the 'df' parameter."""
    def decorator(*args, **kwargs):
        if 'df' not in kwargs:
            raise ValueError(
                "The function should have and return a single dataframe called 'df'")
        id_original = id(kwargs['df'])
        returned_df = func(*args, **kwargs)
        id_returned = id(returned_df)
        if not id_original == id_returned:
            raise ValueError(
                'A copy of the dataframe was made. Check for typecasting.')
        return returned_df
    return decorator


class DataframeParser:
    """Provides a common interface to extract information on each table.

    Attributes:
        file_path (str): Path to the .txt file containing the data.
        nrow_head (int): Number of rows to include in the DataframeParser.head. For the first-pass dtype/schema inference.
        prettify_names (bool): If True, sanitize column and table names.
    """
    def __init__(self, file_path, nrow_head=100, prettify_names=True):
        self.file_path = validate_path(file_path)
        self.prettify_names = prettify_names

        self._nrow_head = nrow_head
        self._head_df = None
        self._full_df = None


    def _preprocess_dataframe(self, df):
        """Preprocess any dataframe read from DataframeParser.partial_read().

        This is the main method for data preprocessing. All preprocessing steps
        should be implemented as staticmethods or functions and included in this method.
        Any table-specific preprocessing should inherit from DataframeParser and override this method.

        Args:
            df (pandas.DataFrame): The raw data output from DataframeParser._partial_read().

        Returns:
            df (pandas.DataFrame): The cleaned and preprocessed data.
        """
        df = self.infer_datetime_types(df)
        df = self.format_datetime_cols(df)
        df.columns = [self._prettify_name(col) for col in df.columns]
        return df

    def _partial_read(self, n, encoding='utf-8'):
        """Safely read n lines from self.file_path."""
        with open(self.file_path, 'rb') as fp:
            try:
                # TODO: break this out
                if self.file_path.endswith('.txt'):
                    df = pd.read_table(filepath_or_buffer=fp, nrows=n, encoding=encoding, sep='\t')
                else:
                    df = pd.read_csv(filepath_or_buffer=fp, nrows=n, encoding=encoding)
            except pd.errors.ParserError as e:
                print('Parser error on file: {0}'.format(self.file_path))
                raise e
        return df

    @property
    def head(self):
        if self._head_df is None:
            print('Reading head: {0}'.format(self.file_path))
            df = self._partial_read(n=self._nrow_head)
            df = self._preprocess_dataframe(df)
            self._head_df = df
        return self._head_df

    @property
    def dataframe(self):
        if self._full_df is None:
            print('Reading full: {0}'.format(self.file_path))
            df = self._partial_read(n=None)
            df = self._preprocess_dataframe(df)
            self._full_df = df
        return self._full_df

    @property
    def columns(self):
        cols = self.head.columns
        return cols.tolist()

    @property
    def dtypes(self):
        return self.head.dtypes.tolist()

    @property
    def primary_key(self):
        return self.columns[0]

    @property
    def name(self):
        """Name of the SQL table, derived from the filename."""
        name = get_filename(self.file_path)
        if self.prettify_names:
            name = self._prettify_name(name)
        return name

    def _prettify_name(self, string):
        string = remove_numeric_head(string)
        string = make_valid_name(string)
        return string

    @staticmethod
    def _safe_to_datetime(col):
        """Convert column to datetime."""
        # TODO: add more checks / tests for common date formats
        col = pd.to_datetime(col, infer_datetime_format=True)
        return col

    @staticmethod
    def infer_datetime_types(df):
        """Infer datetimes by the column name."""
        for col in df:
            col_str = str(col).lower()
            if 'date' in col_str:
                df[col] = DataframeParser._safe_to_datetime(df[col])
        return df

    @staticmethod
    def format_datetime_cols(df):
        def _format_if_datetime(col):
            if is_datetime64_any_dtype(col.dtype):
                format_dates = lambda x: x.strftime('%Y-%m-%d') if not pd.isna(x) else x
                return col.map(format_dates)
            else:
                return col
        df = df.apply(_format_if_datetime, axis=0)

        return df
