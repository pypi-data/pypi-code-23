"""
Generate SQLAlchemy code to declare the database's schema.
This strategy takes advantage of pandas type inference on columns.
"""

import datetime
import os
import time

from autoalchemy.dataframe_parser import DataframeParser
from autoalchemy.utils import make_valid_name
from pandas.api.types import is_datetime64_any_dtype

# Templates for generating SQLAlchemy table declarations
CLASS_TEMPLATE = \
"""
class {class_name}(Base):
    __tablename__ = '{table_name}'
{columns}
""".strip()

COLUMN_TEMPLATE = '{name} = Column({dtype})'

PRIMARY_KEY_TEMPLATE = '{name} = Column({dtype}, primary_key=True)'

# Other constants
TABCHAR = '    '  # 4 spaces

# Preamble to file
IMPORTS = \
"""
from sqlalchemy import Column, ForeignKey, Integer, Float, Date, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
""".strip()

BASE_DECLARATION = \
"""
Base = declarative_base()
""".strip()

WARNING = \
'''
"""
CREATED AT: {date}
THIS CODE IS GENERATED AUTOMATICALLY. DO NOT MODIFY THIS FILE.

REGENERATE THIS FILE USING schema_code_generator.py EACH TIME THE DATABASE IS CREATED.
"""
'''.strip().format(date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

PREAMBLE = [WARNING, '\n', IMPORTS, '\n\n', BASE_DECLARATION, '\n\n']


def pandas_to_sql_type(dtype):
    """Convert the datatype from pandas to SQLAlchemy notation."""
    # TODO: see if we can do a better job on the dtypes
    if dtype == 'int64':
        code_dtype = 'Integer()'
    elif dtype == 'float64':
        code_dtype = 'Float()'
    elif dtype == 'object':
        code_dtype = 'String(250)'
    elif is_datetime64_any_dtype(dtype):
        code_dtype = 'Date()'
    else:
        raise ValueError('Dtype not recognized: {0}'.format(dtype))
    return code_dtype


def table_code(dfparser, i):
    """Take the metadata from a single dataframe and generate declarative code for its SQL table.

    Args:
        dfparser (DataframeParser): An object of type DataframeParser
        i (int): The number of the class, only to be used as a classname.
    """
    class_name = 'Class_{0}'.format(i)
    table_name = dfparser.name

    column_code_lines = []
    for col, dtype in zip(dfparser.columns, dfparser.dtypes):
        code_dtype = pandas_to_sql_type(dtype=dtype)
        template = PRIMARY_KEY_TEMPLATE if (col == dfparser.primary_key) else COLUMN_TEMPLATE
        column_code = template.format(name=make_valid_name(col), dtype=code_dtype)
        column_code_lines.append(column_code)

    # each columns should be preceded by a newline and tab
    whitespace = '\n' + TABCHAR
    column_code = whitespace.join(column_code_lines)
    column_code = whitespace + column_code  # first line doesn't get the join string

    return CLASS_TEMPLATE.format(class_name=class_name, table_name=table_name, columns=column_code)


def generate_sqlalchemy_schema_code(df_list, out_file):
    """Generate Python code to define the schema."""
    if not isinstance(df_list[0], DataframeParser):
        raise ValueError('Input must be a list of DataframeParser objects.')

    with open(out_file, 'w') as fp:
        # Write warnings and imports first
        fp.writelines(PREAMBLE)

        for i, dfparser in enumerate(df_list):
            generated_table_code = table_code(dfparser, i)
            fp.write(generated_table_code)
            fp.write('\n\n\n')

    print('GENERATED SCHEMA CODE WRITTEN TO: {0}'.format(out_file))
