# -*- coding: utf-8 -*-
"""
Created on Sun Jan 28 13:27:23 2018

@author: jaredmt
"""

'''=============pandas data analysis=============='''
'''read thru the pandas pdf for data analysis. it has a tutorial section
https://pythonprogramming.net/input-output-data-analysis-python-pandas-tutorial/?completed=/basics-data-analysis-python-pandas-tutorial/
another example is ESPNFHL2.py
pandas is great for analyizing large data sets. 
it can import/export just about any file type
'''
'''
from pandas import DataFrame
web_stats = {'Day':[1,2,3,4,5,6],
             'Visitors':[43,34,65,56,29,76],
             'Bounce Rate':[65,67,78,65,45,52]}#note:dicts autosort
ind=['ind1','ind2','ind3','ind4','ind5','ind6']
df = DataFrame(web_stats,index=ind)
print(df)
df[["Visitors","Bounce Rate"]].plot()
print(df.head(10))#prints the first 10 results of data (default gives 5)

#another example:
import pandas as pd
a={"col1":[1,2,3], "col2":[4,5,6]}
f=pd.DataFrame(a)
f["col3"]=[2,2,2]#add a column
f.loc[3]=[5,4,3]#add a row
print(f)

e1={'hello':['yes','there'],'world':['no','here']}
e2={'hello':['take','values'],'world':['yep','nope']}
i=['ind1','ind2']
df1=DataFrame(data=e1,index=i)
df2=DataFrame(data=e2)
#df=df1.join(df2,lsuffix="1",rsuffix="2")#add dataframe columns
#df=df1.append(df2,ignore_index=True)#add dataframe rows
#df=df1+df2#this adds the data together. similar to adding matrices
#df=df.transpose()# rotates the data (columns=index and vise versa)
#df.axes[0]#all the indexes
#df.axes[1]#all headers
#df.values#returns all data as numpy array
#df.loc[df.index[0]]#get first row
#df.iloc[0]#get first row
#df[df.columns[0]]#get data in first column
#df.index[0]#get first index name


#Add/Remove Data
#df.drop(index[0])#drop first row(input is always index)
#df.drop('ind1')#equivalent to above if index[0]='ind1'
#df=df['Day','Visitors']#remove all but 'Day' and 'Visitors' columns
#df["col3"]=[2,2,2]#add a column
#df.loc[3]=[5,4,3]#add a row
L=[df['ind1':'ind3'],df['ind4':'ind5'],df['ind6':'ind6']]
df=concat(L)#concatinate (add to end) other dataframes rows under the same columns
DataFrame(df['Day']).join(DataFrame(df['Visitors']))#add dataframe columns
df1=df['ind1':'ind2']
df2=df['ind2':'ind3']
dff=df1.append(df2)#the row with 'ind2' is in there twice
dff.drop_duplicates()#(this can be used for queries of 'this' OR 'that')

#Changing values
#df.at['ind1','Day']=15#change the value at this index and column header
#df.iat[0,0]=15#change value at first index and first column header
#df.columns.values[0]='BR'#changes first column name
#df.index.values[0]='i1'#changes first index name
#df.columns=['d1','d2','d3']#change name of entire column
#df.index=['i1','i2','i3','i4','i5','i6']#change name of all indexes
#df.rename(columns={'Day':'D2'})#rename column by name
#df.rename(index={'ind1':'indd1'})#rename row by index name

#plotting
df.plot()#plots the entire dataframe


#examples from special nomenclature:
df=read_excel(filename)
df=df.drop(df.index[-8:])#remove last 8 rows
dffind=df[df['SIZE']==60]#narrows down to only 60" screens
dffind=dffind[dffind['MESH TYPE']=='TB']#narrows down to TBC mesh
dffind=dffind[dffind['Explanation'].str.contains('epoxy')]#narrows down to epoxied screens
print(dffind[['Part Number','Explanation']])#print final query with only 'Part Number'

#writing to excel:
from openpyxl import load_workbook
df = DataFrame(web_stats,index=ind)#data to write to excel
writer = ExcelWriter(file_name)
book=load_workbook(file_name)
#this allows you to add a new sheet to existing workbook
writer.book=book#without this line, it would overwrite the file and delete previous info
df.to_excel(writer, 'NewSheet',index=False)
writer.save()
writer.close()
'''
def DFChangeHeader(df,newheader):
    "df=DataFrame (pandas) and newheader=list or array"
    from pandas import DataFrame
    
    #alg 1
    #oldheader=list(df.columns.values)
    #df=df.rename(columns={oldheader[i]:newheader[i] for i in range(len(oldheader))})
    
    #alg 2
    #df=DataFrame(df.get_values(),columns=newheader,index=df.axes[0])
    
    #alg 3
    df.columns=newheader
    return df

def DFGetData(df):
    "gets DataFrame data and returns as a nested list"
    from pandas import DataFrame
    
    #alg 1
    #header=list(df.columns.values)
    #data=[list(df[header[i]]) for i in range(len(header))]
    
    #alg 2
    data=df.values
    return data

def DFSize(df):
    '''gets size of DataFrame data
    returns [# of indexes, # of columns]'''
    from pandas import DataFrame
    s=[len(df.axes[0]),len(df.axes[1])]
    return s

def DFFind(df={},equals={},contains={},eCaseSensitive=False,cCaseSensitive=False):
    '''returns a dataframe with only the data that meets 'equals' and 'contains'
    dictionaries. not case sensitive by default
    pre requisite: pandas
    DFFind(df={},equals={},contains={},eCaseSensitive=False,cCaseSensitive=False)
    example:
        data1={'size': ["hello","world"], 'shape':['word','two']}
        df=DataFrame(data=data1)
        dfsearch=DFFind(df,contains={'size':["el"]})
        dfsearch=DFFind(df,equals={'size':["hello"]})
    '''
    if len(df)==0:
        error("must input a DataFrame df to search")
    #equalsList=list(equals.values())#get values (not needed)
    containsKeys=list(contains.keys())#get keys
    equalsKeys=list(equals.keys())
    if len(equals)>0:
        for i in range(len(equalsKeys)):
            for j in range(len(equals[equalsKeys[i]])):
                eItem=equals[equalsKeys[i]][j]
                if eCaseSensitive:
                    df=df[df[equalsKeys[i]]==eItem]#case sensitive
                else:
                    f=lambda x: x.astype(str).str.lower()
                    df=df[df.apply(f)[equalsKeys[i]]==str(eItem).lower()]#not case sensitive
                
    if len(contains)>0:        
        for m in range(len(containsKeys)):
            for n in range(len(contains[containsKeys[m]])):
                cItem=contains[containsKeys[m]][n]
                if cCaseSensitive:
                    df=df[df[containsKeys[m]].str.contains(cItem)]#case sensitive
                else:
                    f=lambda x: x.astype(str).str.lower()
                    df=df[df.apply(f)[containsKeys[m]].str.contains(str(cItem).lower())]#not case sensitive
    return df

def DFDropNullRows(df):
    '''deletes null rows'''
    #from math import isnan#only needed in alg 1
    from pandas import DataFrame,isnull
    ind=df.index.values
    #h=df.columns.values#only needed in alg 1
    nanind=[]#start with blank list of indexes
    df2=df
    
    for i in range(len(ind)):
        #alg 1: (only works on numbers)
        #if all([isnan(df[df.index==ind[i]].values[0][j]) for j in range(len(h))]):
            #nanind.append(ind[i])
        #alg 2: (seems to work on anything)
        if all(isnull(df[df.index==ind[i]]).values[0]):#entire row is null
            nanind.append(ind[i])#add this index to the list
    df=df.drop(nanind)#drop all indexes with full null rows
    return df

def DFIfNullConcatDrop(df,ds=""):
    '''checks first column for null values from last to first row
    if null then the text on this row will be concatenated
    to the row above. then the current row will be deleted
    (this function was used to help reformat Final Assy Schedule)
    ds = delimit string (blank by default)'''
    from pandas import DataFrame,isnull
    ind=df.index.values
    for k in range(len(ind)):
        i=-k-1#using i to check from the end to the begining
        if isnull(df.iat[i,0]):#check each value in first column for null
            df=DFConcatStrDrop(df,i-1,i,ds)
            df=DFIfNullConcatDrop(df,ds)
            break
    return df

def DFConcatStrDrop(df,baserow=0,concatrow=1,ds=""):
    '''concat concatrow strings to baserow strings
    then drop concatrow
    ds = delimit string (blank by default)'''
    from pandas import DataFrame
    h=df.columns.values
    br,cr=baserow,concatrow
    for i in range(len(h)):#for current row, check each column
        if type(df.iat[br,i])==type(df.iat[cr,i])==type(""):#if string values
            df.iat[br,i]+=ds+df.iat[cr,i]#concat
    df=df.drop(df.index[cr])#drop concatrow
    return df

def DFaddCatToSubcat(df):
    '''this is for final assy schedule
    first column is main category
    second column is subcategory
    if first column is blank but 2nd isn't
    then copy string from previous col to current'''
    from pandas import DataFrame,isnull
    ind=df.index.values
    for i in range(1,len(ind)):
        if isnull(df.iat[i,0]) and not isnull(df.iat[i,1]):
            df.iat[i,0]=df.iat[i-1,0]
    return df