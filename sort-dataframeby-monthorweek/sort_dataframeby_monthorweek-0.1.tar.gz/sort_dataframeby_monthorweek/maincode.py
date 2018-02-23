# -*- coding: utf-8 -*-
"""
Created on Fri Feb 23 12:24:01 2018

@author: Dinesh
"""

'''
To sort a dataframe by month name or by weekday name in chronological order (not in alphabatical order) 
below functions are cretaed.
'''
# imports which are required for below functions
import pandas as pd
import itertools
from sorted_months_weekdays import Month_Sorted_Month,Weekday_Sorted_Week

# the inputs for Sort_Dataframeby_Month function are dataframe, month column name
def Sort_Dataframeby_Month(df,monthcolumnname):
    # using Month_Sorted_Month function and creating sorted list of rows by month
    x = list(itertools.chain(*[df[df[monthcolumnname]==word].values.tolist() for word in Month_Sorted_Month(df[monthcolumnname])]))
    # creating a dataframe with list of rows from x after sorting
    y= pd.DataFrame(x, columns=df.columns.values.tolist())
    # returning final dataframe with sorted months
    return(y)

# the inputs for Sort_Dataframeby_Month function are dataframe, weekday column name
def Sort_Dataframeby_Weekday(df,Weekdaycolumnname):
    # using Weekday_Sorted_Week function and creating sorted list of rows by weekday
    x = list(itertools.chain(*[df[df[Weekdaycolumnname]==word].values.tolist() for word in Weekday_Sorted_Week(df[Weekdaycolumnname])]))
    # creating a dataframe with list of rows from x after sorting
    y= pd.DataFrame(x, columns=df.columns.values.tolist())
    # returning final dataframe with sorted weekdays
    return(y)


# the inputs for Sort_Dataframeby_MonthandNumeric_cols are dataframe, month column name & Numeric column
def Sort_Dataframeby_MonthandNumeric_cols(df,monthcolumn,numericcolumn):
    # creating a new dataframe with only month column and numeric column
    df1 = df[[monthcolumn,numericcolumn]]
    # using Month_Sorted_Month function and creating sorted list of rows by month
    x = list(itertools.chain(*[sorted(df1[df1[monthcolumn]==word].values.tolist()) for word in Month_Sorted_Month(df1[monthcolumn])]))
    # creating another dataframe with the above list which we get after sorting (This dataframe will have only sorted month column and sorted numeric column)
    y = pd.DataFrame(x, columns=df1.columns.values.tolist())
    # Merging sorted dataframe with original dataframe to concatenate extra columns
    z = pd.merge(y,df)
    # removing duplicates if any after merging
    z = z.drop_duplicates()
    # after removing duplicates need to reset the index
    z = z.reset_index()
    # deleting the original index and keeping new index
    del z['index']
    # returning final dataframe with sorted months and numerics
    return(z)

# the inputs for Sort_Dataframeby_MonthandNumeric_cols are dataframe, weekday column name & Numeric column
def Sort_Dataframeby_WeekandNumeric_cols(df,weekdaycolumn,numericcolumn):
    # creating a new dataframe with only weekday column and numeric column
    df1 = df[[weekdaycolumn,numericcolumn]]
    # using Weekday_Sorted_Week function and creating sorted list of rows by weekday
    x = list(itertools.chain(*[sorted(df1[df1[weekdaycolumn]==word].values.tolist()) for word in Weekday_Sorted_Week(df1[weekdaycolumn])]))
    # creating another dataframe with the above list which we get after sorting (This dataframe will have only sorted weekday column and sorted numeric column)
    y = pd.DataFrame(x, columns=df1.columns.values.tolist())
    # Merging sorted dataframe with original dataframe to concatenate extra columns
    z = pd.merge(y,df)
    # removing duplicates if any after merging
    z = z.drop_duplicates()
    # after removing duplicates need to reset the index
    z = z.reset_index()
    # deleting the original index and keeping new index
    del z['index']
    # returning final dataframe with sorted months and numerics
    return(z)
    