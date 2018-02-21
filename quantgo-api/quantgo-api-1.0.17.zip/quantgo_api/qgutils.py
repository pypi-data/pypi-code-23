import os
import gzip
import time
import boto3

from multiprocessing.pool import ThreadPool

DOWNLOAD_DELAY = 5
#DOWNLOAD_TIMEOUT = 600
DOWNLOAD_TIMEOUT = 0

def download_task(task):
    access_key = task['access_key']
    secret_key = task['secret_key']
    profile_name = task['profile_name']
    bucket = task['bucket']
    key = task['key']
    fpath = task['fpath']
    uncompress = task['uncompress']
    session = boto3.Session(aws_access_key_id=access_key, aws_secret_access_key=secret_key, profile_name=profile_name)
    s3 = session.client('s3')
    start = time.time()
    
    tmp_fpath = fpath
    if uncompress:
        tmp_fpath = '%s.tmp' % (fpath)
    exists = False
    if task['debug']:
        print('Downloading %s' % (key))
    while True:
        try:
            s3.download_file(bucket, key, tmp_fpath, {'RequestPayer':'requester'})
            exists = True
            break
        except Exception as e:
            if e.response['Error']['Code'] == "NoSuchKey" or e.response['Error']['Code'] == "404":
                exists = False
                break
            else:
                if time.time() - start >= DOWNLOAD_TIMEOUT:
                    raise e
                time.sleep(DOWNLOAD_DELAY)
    if exists and uncompress:
        with gzip.open(tmp_fpath, 'rb') as inf:
            with open(fpath, 'wb') as outf:
                while 1:
                    block = inf.read(size=1024)
                    if not block:
                        break;
                    outf.write(block)
        os.remove(tmp_fpath)
    task['exists'] = exists
    return task

def download_async(num_threads, tasks):
    if not tasks:
        return
    res_tasks = []
    if num_threads > 1:
        pool = ThreadPool(processes=num_threads)
        for task in pool.imap_unordered(download_task, tasks):
            if task['debug']:
                if task['exists']:
                    print('Downloaded %s' % (task['key']))
                else:
                    print('Not found %s' % (task['key']))
            res_tasks.append(task)
        pool.terminate()
    else:
        for task in tasks:
            task = download_task(task)
            if task['debug']:
                if task['exists']:
                    print('Downloaded %s' % (task['key']))
                else:
                    print('Not found %s' % (task['key']))
            res_tasks.append(task)
    return res_tasks