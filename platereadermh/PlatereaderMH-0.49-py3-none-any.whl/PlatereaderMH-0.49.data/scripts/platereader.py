#!python

# coding: utf-8

import pandas as pd
import numpy as np
import os
import re
import subprocess
import sys
from datetime import datetime, date, time, timedelta

pd.options.mode.chained_assignment = None  # default='warn'

if len(sys.argv) == 1:
    print('Put in filepath.')
    sys.exit()._exit()
if len(sys.argv) == 2:
    filepath = sys.argv[1]
    hfile = 'empty'
    print(filepath)
if len(sys.argv) == 3:
    filepath = sys.argv[1]
    hfile = sys.argv[2]
    print(filepath, hfile)


import string
string.ascii_uppercase
plate_row = pd.DataFrame(list(string.ascii_uppercase), columns=['plate_row'])[0:9]
plate_row['row'] = plate_row.index

#load data

df = pd.read_table(filepath, decimal =',', encoding = "ISO-8859-1", header=2)
if df.keys().values[-1] == 'Unnamed: 15': #check if header was correctly skipped
    df = df.drop(['Temperature(¡C)', 'Unnamed: 14', 'Unnamed: 15'], axis=1) #drop needless columns
    a = df.columns[0]
    df= df[:-2] #drop last 2 rows which contain needless strings
else:
    df = pd.read_table(filepath, decimal =',', encoding = "ISO-8859-1", header=4)
    df = df.drop(['Temperature(¡C)', 'Unnamed: 14', 'Unnamed: 15'], axis=1)
    a = df.columns[0]
    df= df[:-2] #drop last 2 rows which contain needless strings

# for time course measurements
if a == 'Time(hh:mm:ss)':
    b = 'time (s)'
    df = df.rename(columns = {a:b})
    a = b
    df[a] = df[a].fillna(method='ffill',limit=7) # value for rows B to G of 96 well
    df = df.dropna(axis=0, how='all') #drop empty line
    #format datetime...different format after 1h
    df1 = df[df[a].str.contains('^\d*:\d*$')]
    df1[a] = pd.to_datetime(df1[a], format= '%M:%S')

    df2 = df[df[a].str.contains('^\d*:\d*:\d*$')]
    df2[a] = pd.to_datetime(df2[a], format= '%H:%M:%S')

    df = pd.concat([df1, df2])
    #get time differences in total seconds
    df[a] = df[a]-df[a].min()
    df[a] = df[a].dt.total_seconds()
    df['row'] = df.groupby(a).cumcount()
    df= pd.merge(df, plate_row, on = 'row').drop(['row'], axis = 1).sort_values([a]).reset_index(drop=True)
    df = df.melt(id_vars=['plate_row', a], var_name = 'plate_column').dropna()

# for spectra measurements
if a == 'Wavelength(nm)':
    df[a] = df[a].astype('float')
    df[a] = df[a].fillna(method='ffill',limit=7)
    df = df.dropna(axis=0, how='all')
    df['row'] = df.groupby(a).cumcount()
    df= pd.merge(df, plate_row, on = 'row').drop(['row'], axis = 1).sort_values([a]).reset_index(drop=True)
    df = df.melt(id_vars=['plate_row', a], var_name = 'plate_column').dropna()

# for single point measurements
if a == 'Unnamed: 0':
    df = df.dropna(axis=0, how='all')
    df['row'] = df.groupby(a).cumcount()
    df = df.drop([a], axis=1)
    df= pd.merge(df, plate_row, on = 'row').drop(['row'], axis = 1).reset_index(drop=True)
    df = df.melt(id_vars=['plate_row'], var_name = 'plate_column').dropna()


#back to wide-table format

while True:
    if hfile == 'empty':
        if a == 'Unnamed: 0':
            a= 'plate_row'
            df['sample'] = df['plate_row']+df['plate_column']
            df['time (s)'] = 'Endpoint'
            df = df.pivot_table(index=[a], columns = ['plate_column'], values= 'value').reset_index().rename_axis(None, 1)
            break
        else:
            df['sample'] = df['plate_row']+df['plate_column']
            df = df.pivot_table(index=[a], columns = ['sample'], values= 'value').reset_index().rename_axis(None, 1)
        break
    else:
        plate = pd.read_excel(hfile)
        #to long table format, drop needless columns
        plate = plate.melt(id_vars=['plate_row'], var_name = 'plate_column', value_name='sample').dropna()
        plate['plate_column'] = plate['plate_column'].astype('int')
        plate['plate_row'] = plate['plate_row'].astype('str')
        #with helper file
        df.merge(plate, on = 'plate_row')
        df['plate_column'] = df['plate_column'].astype('int')
        well = ['plate_row','plate_column']
        df = pd.merge(df, plate, on = well)
        if a == 'Unnamed: 0':
            a= 'time (s)'
            df[a] = 'Endpoint'
            df = df.pivot_table(index=[a], columns = ['sample'], values= 'value').reset_index().rename_axis(None, 1)
            break
        else:
            df = df.pivot_table(index=[a], columns = ['sample'], values= 'value').reset_index().rename_axis(None, 1)
            break

###sort columns
def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    def atoi(text):
        return int(text) if text.isdigit() else text

    return [atoi(c) for c in re.split('(\d+)', text)]

columns = df.keys()
df = df.reindex(columns=sorted(df.columns, key=natural_keys))

col = df[a]
df.drop([a], axis=1,inplace = True)
df.insert(0, a, col)

#export data to excel

filename = os.path.splitext(filepath)[0]+'.xlsx'
folder = os.path.dirname(filename)


writer = pd.ExcelWriter(filename)
df.to_excel(writer)
writer.save()

#args = ['open', folder]
#subprocess.check_call(args)
print('File saved as:')
print(filename)
print('Done.')
