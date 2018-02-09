import pandas as pd

results = []
for i in range(5):
    result = []
    for x in range(3):
        result.append(i * x)
    results.append(result)

df = pd.DataFrame(results)
df.columns = ['a', 'b', 'c']
