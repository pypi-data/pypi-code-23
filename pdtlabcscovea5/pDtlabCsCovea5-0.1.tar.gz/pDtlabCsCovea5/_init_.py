#!/usr/bin/python2.7
#-*- coding: utf-8 -*-

from datetime import datetime
from git import Git, Repo 
from gitdb import *
import pexpect
import sys
import os

def hello_word():
    print("hello world")