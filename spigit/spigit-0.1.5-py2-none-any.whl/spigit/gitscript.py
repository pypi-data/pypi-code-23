#!/usr/bin/python2.7
import os
import time
import logging
import datetime
import json
from subprocess import Popen, PIPE
import git

try:
    with open("~/initspigit" + "/gitscriptconfig.json") as json_data_file:
        config = json.load(json_data_file)
except Exception as e:
    print(str(e))

BRANCH = config["repoinfo"]["BRANCH"]
REMOTE_URL = config["repoinfo"]["REMOTE_URL"]

UPDATE_INTERVAL = config["varinfo"]["UPDATE_INTERVAL"]

LOG_FILE = config["localinfo"]["LOG_FILE"]
REPO_NAME = config["localinfo"]["REPO_NAME"]
REPO_PATH = config["localinfo"]["REPO_PATH"]
REPO_OWNER = config["localinfo"]["REPO_OWNER"]
REPO_OWNER_ID = config["localinfo"]["REPO_OWNER_ID"]
REPO_OWNER_GRPID = config["localinfo"]["REPO_OWNER_GRPID"]

command_b4 = config["appinfo"]["CMD_BEFORE_PULL"]
command_af = config["appinfo"]["CMD_AFTER_PULL"]

LOG_PATH = REPO_PATH + LOG_FILE
DIR_FULL = REPO_PATH + REPO_NAME

if __name__ == '__main__':
    #//Setup config
    try:
        logging.basicConfig(filename=LOG_PATH, level=logging.INFO)
        logging.info(str(datetime.datetime.now()) + " - Service started")
    except:
        os.makedirs(REPO_PATH)
        logging.basicConfig(filename=LOG_PATH, level=logging.INFO)
        logging.info(str(datetime.datetime.now()) + " - Start of Log file")
        logging.info(str(datetime.datetime.now()) + " - Service started")
    #//Main loop
    while True:
        #//Run commands in bash as root before attempted pull
        if command_b4 != ['']:
            for cmd in command_b4:
                try:
                    p = Popen(cmd, stdout=PIPE, shell=True)
                except Exception as e:
                    logging.error(str(datetime.datetime.now()) + " - Couldn't execute CMD_BEFORE_PULL. " + "Error: " + str(e))
        #//
        #//Clone the Repo if the directory doesnt already exsist
        if not os.path.isdir(DIR_FULL):
            try:
                repo = git.Repo.clone_from(REMOTE_URL, DIR_FULL, branch=BRANCH)
                logging.info(str(datetime.datetime.now()) + " - Repo Cloned from " + REMOTE_URL)
                #//Give permissions to the cloned dirs and files
                try:
                    if REPO_OWNER and REPO_OWNER != "root":
                        os.chown(DIR_FULL, REPO_OWNER_ID, REPO_OWNER_GRPID)
                        for root, dirs, files in os.walk(DIR_FULL):
                          for dirz in dirs:
                            os.chown(os.path.join(root, dirz), REPO_OWNER_ID, REPO_OWNER_GRPID)
                          for filez in files:
                            os.chown(os.path.join(root, filez), REPO_OWNER_ID, REPO_OWNER_GRPID)
                except Exception as e:
                    logging.error(str(datetime.datetime.now()) + " - Setting repo permissions failed. " + "Error: " + str(e))
                #//
            except Exception as e:
                logging.error(str(datetime.datetime.now()) + " - Cloning repo fail from gitscriptconfig.json. " + "Error: " + str(e))
        #//
        else:
            #//Pull the repo if the path exsists
            try:
                repo = git.Repo(DIR_FULL)
                #//If the working directory is not clean, send info to logging
                if repo.git.diff() == "":
                    repo.git.pull()
                #//
                else:
                    logging.info(str(datetime.datetime.now()) + " - Pull failed; Make sure your working directory is clean to pull")
            except Exception as e:
                logging.error(str(datetime.datetime.now()) + " - Pulling repo fail from gitscriptconfig.json. " + "Error: " + str(e))
            #//
        #//Run commands as root after attempted pull
        if command_b4 != ['']:
            for cmd in command_af:
                try:
                    p = Popen(cmd, stdout=PIPE, shell=True)
                except Exception as e:
                    logging.error(str(datetime.datetime.now()) + " - Couldn't execute CMD_AFTER_PULL. " + "Error: " + str(e))
        #//
        time.sleep(UPDATE_INTERVAL)
