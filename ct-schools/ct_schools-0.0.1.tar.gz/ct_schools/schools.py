from fuzzywuzzy import fuzz, process
import os
import pandas as pd

cached = None

def schooldf():

    global cached

    dir_path = os.path.dirname(os.path.realpath(__file__))

    if cached is None:
        cached = pd.read_csv(os.path.join(dir_path, "data","schools.csv"))

    return cached

def name_col():
    df = schooldf()
    return df["School Name"]

def clean_name(n):
    return n.upper().strip()

def clean_series(s):
    return s.apply(clean_name)

def clean_name_col():
    return clean_series(name_col())

def fuzz_ratio(a, b):
    return fuzz.ratio(clean_name(a), clean_name(b))

def fuzz_min(a, b, min_ratio=90):

    return fuzz_ratio(a,b) > min_ratio

def fuzz_df(name):

    df = schooldf()

    df["FUZZ_RATIO"] = df["School Name"].apply(lambda x: fuzz_ratio(x, name))

    return df

def __school_by_name_closest(name):

    df = fuzz_df(name)

    return df.sort_values(by="FUZZ_RATIO", ascending=False).head(1)
                                               

def __school_by_name_exact(name):
    df = schooldf()
    ret = df[clean_name_col() == clean_name(name)]

    if len(ret) < 1:
        raise Exception("School not found")
    if len(ret) > 1:
        raise Exception("Multiple schools found")
    return ret

def __school_by_name_contains(name):
    df = schooldf()
    ret = df[clean_name_col().str.contains(clean_name(name))]
    return ret

def school_by_name(name, partial=True, min_fuzz=None, closest=True):

    if closest is not False:
        return __school_by_name_closest(name)

    if partial is False:
        return __school_by_name_exact(name)
    
    if min_fuzz is not None and type(min_fuzz) is int:
        return __school_by_minfuzz(name, min_fuzz)

    # default
    return __school_by_name_contains(name)

