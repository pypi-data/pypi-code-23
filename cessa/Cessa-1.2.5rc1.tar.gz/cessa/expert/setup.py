#!/usr/bin/env python3
# encoding: utf-8

import shutil
from pyke import knowledge_engine
from os.path import isdir
from time import sleep

if isdir('compiled_krb'):
    shutil.rmtree('compiled_krb')
sleep(1)
engine = knowledge_engine.engine(__file__)
# engine.activate('bc_relate')
