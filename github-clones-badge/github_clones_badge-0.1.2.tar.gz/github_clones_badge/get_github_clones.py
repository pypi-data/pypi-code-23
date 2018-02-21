import requests
from requests.auth import HTTPBasicAuth
import json
import pickle 
import sys
import os
try:
    from urllib import FancyURLopener
except ImportError:
    from urllib.request import FancyURLopener

import crontab

global DATADIR
DATADIR = os.path.dirname(os.path.realpath(__file__))+"/data/"

class git_creds(object):
    def __init__(self,username=None, password=None, gitfile='git_creds'):
        self.username=username
        self.password=password
        if not username or not password:
            self.get_creds(gitfile)

    def get_creds(self, creds_file='git_creds'):
        creds=[]
        with open(creds_file,'r') as auth_file:
            for l in auth_file:
                creds.append(l.strip())
        self.username=creds[0]
        self.password=creds[1]


class git_clones_counter(object):
    def __init__(self, reponame, username=None, password=None):
        self.count=0
        self.color='gray'
        if not username:
            self.username=git_creds( gitfile='git_creds').username
        if not password:
            self.password=git_creds( gitfile='git_creds').password
        self.repo=reponame
        if not os.path.exists(DATADIR+self.repo+'_clones.pkl'):
            self.initialize_repo()
        self.clones={}
        self.get_previous_clones()

    def initialize_repo(self):
        if os.path.exists(DATADIR+self.repo+'_clones.pkl'):
            os.remove(DATADIR+self.repo+'_clones.pkl')
        pickle.dump({},open(DATADIR+self.repo+'_clones.pkl','w'))

    def get_previous_clones(self):
        self.clones=pickle.load(open(DATADIR+self.repo+'_clones.pkl','rb'))

    def get_git_clones_json(self,username=None):
        if not username:
            username=self.username
        url="https://api.github.com/repos/"+username+"/"+self.repo+"/traffic/clones"
        output=requests.get(url,auth=HTTPBasicAuth(self.username,self.password))
        if output.__getstate__()['status_code'] != 200:
            if output.__getstate__()['status_code'] == 401:
                print("Invalid Username/Password!")
            elif output.__getstate__()['status_code'] == 403:
                print("Empty Password!")
            output.raise_for_status()
        return output
        
    def parse_clones_json(self,json_output):
        if not 'clones'in json_output.json().keys():
            print("No clones returned by GitHub")
            return
        for item in json_output.json()['clones']:
            self.clones[item['timestamp']]=item['count']
        if len(self.clones.keys()) >= len(pickle.load(open(DATADIR+self.repo+'_clones.pkl','rb'))):
            pickle.dump(self.clones,open(DATADIR+self.repo+'_clones.pkl','wb'))

    def count_clones(self):
        s=0
        for i in self.clones.keys():
            s+=self.clones[i]
        self.count=str(s)
        if s==0:
            self.color='red'
            return
        if s<10:
            self.color="orange"
            return
        if s<100:
            self.color="yellow"
            return
        if s<1000:
            self.color="yellowgreen"
            return
        elif s<1000000:
            self.count=str(s/1000)+"K+"
            self.color="green"
            return
        elif s<1000000000:
            self.count=str(s/1000)+"M+"
            self.color="brightgreen"
 

class badge_creator(object):
    def __init__(self,repo,username=None,password=None,repouser=None):
        self.clones=git_clones_counter(repo,username,password)
        if repouser:
            new_clones=self.clones.get_git_clones_json(username=repouser)
        else:
            new_clones=self.clones.get_git_clones_json()
        print(str(len(new_clones.json()['clones']))+ " Number of new entries")
        self.clones.parse_clones_json(new_clones)
        self.clones.count_clones() 
        self.count=self.clones.count
        self.color=self.clones.color

    def download_badge(self,dest_path="/var/www/html/apmechev.com/public_html/img/git_repos/"):
        mopen = MyOpener()
        mopen.retrieve("https://img.shields.io/badge/clones-"+self.count+"-"+self.color+".svg",dest_path+"/"+self.clones.repo+"_clones.svg")
        print("done")

class MyOpener(FancyURLopener):
    version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'

