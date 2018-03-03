#!//anaconda/envs/ML3/bin/python
from pymongo import MongoClient
import pandas as pd
import os
import subprocess
import sys
from tqdm import tqdm
from datetime import datetime

LOGFILE = 'transfer2db.log'

def main(path):
    client, db, collection = open_connection()
    paths = get_file_list(path)
    for i, ((flag, lightcurve), file) in tqdm(enumerate(zip(read_lightcurves(paths), paths)), total=len(paths)):
        if flag is True:
            data = get_dict(lightcurve, i)
            insert_data(collection, data)
        else:
            with open(LOGFILE, 'a') as f:
                f.write("[{} -- ERROR]: Unable to read {}\n".format(datetime.now(), file))

def get_dict(df, index):
    data = dict()
    for key in df:
        data[key] = df[key].tolist()
    data['numerical_index'] = index
    data['size'] = len(df)
    return data


def get_file_list(path):
    files = os.listdir(path)
    paths = ["{}/{}".format(path, x) for x in files]
    return paths

def open_connection():
    client = MongoClient()
    db = client['AstronomyData']
    collection = db['PTFData']
    return client, db, collection

def insert_data(collection, data):
    collection.insert_one(data)

def read_lightcurves(files):
    for file in files:
        if file[-3:] == '.lc':
            csv = pd.read_csv(file)
            csv = csv.sort_values('obsHJD')
            yield True, csv
        else:
            csv = None
            yield False, csv

if __name__ == '__main__':
    path = sys.argv[1]
    try:
        with open('MongoDB.log', 'w') as f:
            mongodb = subprocess.Popen(["mongod"], stdout=f)
        main(path)
    finally:
        mongodb.terminate()

