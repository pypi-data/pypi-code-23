# -*- author: Dimitri Scheftelowitsch -*-
# -*- coding:utf-8 -*-


"""
@package collider

A software experimenting framework

@copyright Dimitri Scheftelowitsch
"""

from .stage import Stage, ExecutableStage, ExecutableFileOutputStage
from .resultlog import ResultLog, RunResult
from .predicates import *
from .iteration import run_experiments
from .version import __version__
