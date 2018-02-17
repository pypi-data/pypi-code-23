import pandas as pd
from crosscompute.exceptions import DataTypeError


class EmptyTableError(pd.errors.EmptyDataError, DataTypeError):
    pass
