'''
.. module:: entree.projects
.. moduleauthor:: Julien Spronck
.. created:: Feb 2018

Module for all projects
'''

from entree.projects.base import ProjectBase
from entree.projects.flask import Flask
from entree.projects.flask_large import FlaskLarge
from entree.projects.html5 import HTML5
from entree.projects.python import Python
from entree.projects.sqlalchemy import SQLAlchemy

CLASSES = ProjectBase.__subclasses__()
CLASS_LONG_NAMES = sorted([pcls.project_long_name for pcls in CLASSES])
CLASSES = {pcls.__name__.lower(): pcls for pcls in CLASSES}
