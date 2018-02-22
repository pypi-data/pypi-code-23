import requests
from bs4 import BeautifulSoup
import json
import os
import csv


def request_fun(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html5lib')
    return soup


def save_json(filename,data):
    with open(filename, "w") as jsonFile:
        json.dump(data, jsonFile, sort_keys=True, indent=4,
                  ensure_ascii=False)


## Read From CSV (First Col in done)
def read_done_csv(filename):
    done = []
    if (os.path.exists(filename)):
        with open(filename, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    done.append(row[0])
                except IndexError:
                    continue
    return done


## Read From CSV (First Col in done)
def read_full_csv(filename):
    done = []
    if (os.path.exists(filename)):
        with open(filename, 'rb') as f:
            reader = csv.reader(f)
            for i,row in enumerate(reader):
                if i == 0:
                    pass
                else:
                    try:
                        done.append(row)
                    except IndexError:
                        continue
    return done


## Save to CSV
def save_to_csv(filename, data):

    with open(filename, 'ab') as f:
        writer = csv.writer(f)
        try:
            writer.writerow(data)
        except:
            new_data = [x.encode('utf-8') for x in data]
            writer.writerow(new_data)