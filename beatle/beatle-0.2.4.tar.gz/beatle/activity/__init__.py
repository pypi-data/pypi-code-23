# -*- coding: utf-8 -*-


from . import models
from . import arch
from . import tasks
from . import git
from . import targets

ALL = [models,arch, tasks,git,targets]

VIEWS = [x.ui.view.VIEW for x in ALL]

# VIEWS = [
#     models.ui.view.ModelsView,
#     arch.ui.view.FilesView,
#     tasks.ui.view.TasksView,
#     git.ui.view.GitView,
#     targets.ui.view.TargetsView,
#     ]

INDEX = dict([(x.name, x) for x in VIEWS])

def init():
    """Initialize activities"""
    for activity in ALL:
         activity.init()
