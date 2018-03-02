from splits.s3 import *
print(S3().getstring('s3://stitchfix.aa.warehouse/dw/prod/item/.metadata'))
f = S3File('s3://stitchfix.aa.warehouse/dw/prod/item/.metadata')
for i in f.readlines():
    print(i)


from r2d2 import df_to_hive
import pandas as pd
df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
df_to_hive(df, 'kurt', 'table7')
