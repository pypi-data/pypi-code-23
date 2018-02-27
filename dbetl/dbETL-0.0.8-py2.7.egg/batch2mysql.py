import pandas as pd
import pymysql
from time import time
import os
from secret import dburl, dbusername, dbpasswd




def getDF(diary_id):
    diary_map={1:'diary_2',2:'diary_3',3:'diary_8',4:'diary_9'}
    fl = [i for i in os.listdir(path) if i.startswith(diary_map[diary_id])]
#     print len(fl)
    fl = [i for i in fl if os.stat(path+i).st_size/1024/1024.0>1.5]
#     print len(fl)
    
    coll=[]
    for i in fl:
        df0 = pd.read_csv(path+i)
        df0['serial']=int(i.split('_')[-1].split('.csv')[0])
        coll.append(df0)
        del df0
    print len(coll)

    df = pd.concat(coll,axis=0)
    print df.shape
    print 'remove null post_id'
    df = df[(~df['post_ID'].isnull())]
    print df.shape    
    
    seq = sorted(df['serial'].unique())
    date = ['2018-02-21','2018-02-22','2018-02-23','2018-02-24','2018-02-25']
    times = {i:j for i,j in zip(seq,date)}
    df['date']=df['serial'].map(times)
    
    df['post_ID'] = df['post_ID'].astype('int')
    print 'drop duplicates'
    print df.shape
    df = df.drop_duplicates()
    print df.shape
    df = df[['post_ID','date','comments','favor','views']]
    
    return df


    
    

db = pymysql.connect(host=dburl,    # your host, usually localhost
                     user=dbusername,         # your username
                     passwd=dbpasswd,  # your password
                     port=3306,
                     db="research",
                     charset='utf8')

cur=db.cursor()

def BatchInsert(df):
    
    df=df[['post_ID','date','comments','favor','views']]
    batch = [df.iloc[n*10000:(n+1)*10000,:] for n in range(0 ,int(df.shape[0]/10000.0)+1)]
    
    print 'batch length',len(batch)
    start=time()
    n=0
    for d in batch:
        
        sql = """insert ignore into monitorpost values {}""".format(str(map(lambda x: tuple(x),d.values))[1:-1])
        n+=1
        cur.execute(sql)
        db.commit()
        print n,':{:.2f}s '.format(time()-start),
        start=time()

    
if __name__=='__main__':
    path='data/'
    path=raw_input('path of csv files: ')
    if path[-1]!='/':
        path=path+'/'
    
    diary_loop = 4
    start=time()
    for i in range(1,diary_loop+1):
        print 'start:',i
        df = getDF(i)
        BatchInsert(df)
        del df
        print 'used {:.2f} s '.format(time()-start)
        start=time()