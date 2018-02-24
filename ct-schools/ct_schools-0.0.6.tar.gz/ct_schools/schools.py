"""
 API functions for retrieving school data
"""

from helpers import *

def closest(name, lim=1):
    """
    Get the closest [lim] schools based on the given name
    """

    df = fuzz_df(name)

    return df.sort_values(by="FUZZ_RATIO", ascending=False).head(lim)

def exact(name):
    """
    Find the closest exact (case-insensitive) matching school
    """
    
    df = schooldf()
    ret = df[clean_name_col() == clean_name(name)]

    if len(ret) < 1:
        raise Exception("School not found")
    if len(ret) > 1:
        raise Exception("Multiple schools found")
    return ret
    

def contains(name):
    """
    Find schools whose names contain the given name string (case-exact)
    """
    
    df = schooldf()
    ret = df[clean_name_col().str.contains(clean_name(name))]
    return ret
    
def fuzzy(name, ratio=75):
    """ Find schools with a minimum fuzzywuzzy ratio """
    
    df = fuzz_df(name)

    return df[df["FUZZ_RATIO"] >= ratio].sort_values(by="FUZZ_RATIO",
                                                     ascending=False)
    

def jsonify(df):
    """ Convert DataFrame to json """
    return df.to_json(orient="records")

def dictify(df):
    """ Convert DataFrame to a dict """
    return df.to_dict(orient="records")
