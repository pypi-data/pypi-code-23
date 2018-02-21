import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import pandas_datareader.data as web

style.use('ggplot')

start = dt.datetime(2000,1,1)
end = dt.datetime(2017,12,31)

#dataframe
df = web.DataReader('LREN3.SA', 'yahoo', start, end)

# Print to Debug
#print(df.tail(10))


# Save to CSV file
df.to_csv('tmp/stocks/LREN.csv')


# df = pd.read_csv('tmp/stocks/LREN.csv', parse_dates=True, index_col=0)
