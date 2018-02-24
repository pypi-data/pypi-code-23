"""
Helper functions for importing, searching school data
"""


from fuzzywuzzy import fuzz, process
import os, re
import pandas as pd

cached = None

def schooldf():
    """
    Get the schools dataframe, from disk or cache.
    
      args - none
      rets - Pandas dataframe of all school data
     notes - Always use this to retrieve the data in subsequent
             functions, rather than loading it directly to prevent
             unnecessary disk reads.
    """    

    global cached

    dir_path = os.path.dirname(os.path.realpath(__file__))

    if cached is None:
        cached = pd.read_csv(os.path.join(dir_path, "data","schools.csv"))

    return cached

def name_col():
    """
    Get the school name column as a Pandas Series
    """
    return schooldf()["School Name"]

def clean_name(n):
    """
    Clean a school name for comparison purposes
    """
    return str(n).upper().strip()

def clean_series(s):
    """
    Clean a Pandas Series of school names 
    """
    return s.apply(clean_name)

def clean_name_col():
    """
    Get the school name column from the dataframe and clean it up for
    comparison
    """
    
    return clean_series(name_col())

def fuzz_ratio(a, b):
    """
    Determine the fuzz ratio (see fuzzywuzzy lib) between two strings
    """
    return fuzz.ratio(clean_name(a), clean_name(b))



def fuzz_min(a, b, min_ratio=90):
    """
    Determine whether two strings are at or above the given fuzz ratio
    """
    return fuzz_ratio(a,b) >= min_ratio

def fuzz_df(name):
    """
    Add a FUZZ_RATIO column to the base schools dataframe with the
    ratio between each school's name and the name argument supplied
    """
    
    df = schooldf().copy()

    df["FUZZ_RATIO"] = df["School Name"].apply(lambda x: fuzz_ratio(x, name))

    return df
