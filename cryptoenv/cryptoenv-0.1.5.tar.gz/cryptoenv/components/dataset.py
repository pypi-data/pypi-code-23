import pandas as pd
pd.options.mode.chained_assignment = None

def make_dataset(path, preprocessing_fn):
    df = pd.read_csv(path)

    if not _ohlc_format(df):
        raise ValueError('[ERROR] Dataset is not in ohlc format')
    
    preprocessed = _preprocess(df, preprocessing_fn)
    return df, preprocessed

def _preprocess(df, fn):
    preprocessed = None
    if fn == 'default':
        preprocessed = _preprocess_fn(df)
    return preprocessed

def skip(d_iter, n):
    [next(d_iter) for _ in range(n)]

def _preprocess_fn(df):
    cols = ['close']
    df = df[cols]
    for i in range(1, 12):
        for c in cols:
            df['%s%d' % (c, i)] = df[c].shift(i) / df.loc[:, c]
    for c in cols:
        df[c] = 1.
    return df.dropna()

def _preprocess_fn2(df):
    cols = ['close', 'high', 'low']
    df = df[cols]
    for i in range(1, 50):
        for c in cols:
            df['%s%d' % (c, i)] = df[c].shift(i) / df.loc[:, c]
    for c in cols:
        df[c] = 1.
    return df.dropna()

def _ohlc_format(df):
    cols = df.columns.values
    ohlc = ['open', 'high', 'low', 'close']
    return all(x in cols for x in ohlc)
