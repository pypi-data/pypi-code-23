import requests
from cachecontrol import CacheControl
import json

sess = requests.session()
cached_sess = CacheControl(sess)

def print_log(start=0):
    rl = cached_sess.get("http://localhost:8889/logs/kernel_{0}.log".format(start))
    logs = rl.text.split("\n")
    for log in logs:
        if log:
            jlog = json.loads(log)
            print(jlog["log"])