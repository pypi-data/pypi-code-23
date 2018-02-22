import pandas as pd
from redshiftpandas.date_functions import DateFunctions

dfunc = DateFunctions()

d = {'col1': ['2017-01-01', '2018-02-01']}
df = pd.DataFrame(d)

dfunc.apply_to_df(df,'new_col', 'col1', dfunc.add_months, 1)
print df