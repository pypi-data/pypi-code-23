import requests
import pandas as pd
df = pd.read_html(requests.get('https://en.wikipedia.org/wiki/Ryanair_destinations').content)[1]
df.columns = df.iloc[0]
iatadf = df.reindex(df.index.drop(0))

print ("Done")