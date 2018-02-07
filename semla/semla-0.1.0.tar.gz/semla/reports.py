import pandas_profiling as ppf
import pandas as pd

def get_pandas_profiling_report(df: pd.DataFrame, ):
    ppf.ProfileReport(df)
    pass
