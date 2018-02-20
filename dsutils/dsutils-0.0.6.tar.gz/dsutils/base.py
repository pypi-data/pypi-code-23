import pandas as pd

from sklearn.metrics import roc_auc_score, make_scorer, accuracy_score
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.preprocessing import StandardScaler, Normalizer, MinMaxScaler

from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score

from sklearn import model_selection


from time import strftime, strptime, mktime, time, ctime


def string2second(dt, fmt):
    """
    comvert a string date/time representation to seconds (seconds since the Epoch)
    fillna or wrong time format to '-1'
    e.g. format = '%d/%m/%y' represents input format '23/08/17'
    format examples: 
    https://www.ibm.com/support/knowledgecenter/en/SSEPCD_10.1.0/com.ibm.ondemand.mp.doc/arsa0257.htm
    
    """
    try:
        tmp = strptime(dt, '%d/%m/%y')
        tmp = mktime(tmp)
    except:
        tmp = -1
    return tmp

def extract_date(dt, fmt, sep='/'):
    """
    extract a string date/time to a new string 
    year, month, date, weekday, day of the year, if is Daylight Saving Time, seperates by 'sep'
    e.g. format = '%d/%m/%y' represents input format '23/08/17'
    format examples: 
    https://www.ibm.com/support/knowledgecenter/en/SSEPCD_10.1.0/com.ibm.ondemand.mp.doc/arsa0257.htm
    
    """    
    tmp = strptime(dt, fmt)
    y = tmp.tm_year
    m = tmp.tm_mon
    dy = tmp.tm_mday
    w = tmp.tm_wday
    yd = tmp.tm_yday
    dst = tmp.tm_isdst
    
    return sep.join(map(str,[y,m,dy,w,yd,dst]))


def dfcat2n(train, test):
    """
    convert category data into numeric data of a DF
    input as pandas DataFrame format
    
    """        

    train['Cat']=0
    test['Cat']=1
    print train.shape, test.shape
    
    comb = pd.concat([train, test])
    print comb.shape

    for i in comb.select_dtypes('object'):
        comb[i] = pd.factorize(comb[i])[0]

    train, test = comb[comb['Cat']==0], comb[comb['Cat']==1]
    _, _ = train.pop('Cat'), test.pop('Cat')
    
    return train, test

def dfcat2dummy(train, test, only_keep_mutual=False):
    """
    convert category data into numeric data of a DF
    input as pandas DataFrame format
    
    """        
    train = train.fillna(axis=1, value=-1)
    test = test.fillna(axis=1, value=-1)
    print train.shape, test.shape

    train = train.get_dummies(df)
    test = pd.get_dummies(test)
    
    if only_keep_mutual:
        mul = list(set(df.columns)&set(test.columns))
        train = train.reindex(columns = mul, fill_value=0)
        test = test.reindex(columns = mul, fill_value=0)
        print train.shape, test.shape
        
    else:
        test = test.reindex(columns = train.columns, fill_value=0)
        print train.shape, test.shape
    

    
    return train, test

def strtimeconv(timestr, infmt, outfmt):
    """
    time_string, input_format, output_format
    comvert a string date/time representation to another string with new format
    e.g. format = '%d/%m/%y' represents input format '23/08/17'
    format examples: 
    https://www.ibm.com/support/knowledgecenter/en/SSEPCD_10.1.0/com.ibm.ondemand.mp.doc/arsa0257.htm
    
    """  
    return strftime(outfmt, strptime(timestr, infmt))

def base_main():
    print 'pass'