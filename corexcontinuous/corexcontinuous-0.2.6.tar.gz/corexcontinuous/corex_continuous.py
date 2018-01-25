from sklearn import preprocessing
#import primitive
import sys
import os
import corexcontinuous.linearcorex.linearcorex.linearcorex as corex_cont
#import LinearCorex.linearcorex as corex_cont
from collections import defaultdict, OrderedDict
from scipy import sparse
import pandas as pd
import numpy as np

import d3m_metadata.container as container
import d3m_metadata.hyperparams as hyperparams
import d3m_metadata.params as params
from d3m_metadata.metadata import PrimitiveMetadata

from primitive_interfaces.unsupervised_learning import UnsupervisedLearnerPrimitiveBase
from primitive_interfaces.base import CallResult
#from primitive_interfaces.params import Params
from d3m_metadata.hyperparams import Uniform, UniformInt, Union, Enumeration

from typing import NamedTuple, Optional, Sequence, Any
import typing

Input = container.DataFrame
Output = container.ndarray

class CorexContinuous_Params(params.Params):
    model:typing.Union[corex_cont.Corex, None]
    #fitted: bool
    #training_inputs: Input

    # add support for resuming training / storing model information


class CorexContinuous_Hyperparams(hyperparams.Hyperparams):
    n_hidden = Union(OrderedDict([('n_hidden int' , hyperparams.Uniform(lower = 1, upper = 50, default = 2, q = 1, description = 'number of hidden factors learned')),
        ('n_hidden pct' , hyperparams.Uniform(lower = 0, upper = .50, default = .2, q = .05, description = 'number of hidden factors as percentage of # input columns'))]), 
        default = 'n_hidden pct')


class CorexContinuous(UnsupervisedLearnerPrimitiveBase[Input, Output, CorexContinuous_Params, CorexContinuous_Hyperparams]):  #(Primitive):
    
    """
    Return components/latent factors that explain the most multivariate mutual information in the data under Linear Gaussian model. For comparison, PCA returns components explaining the most variance in the data.  Serves as DSBox 'wrapper' for https://github.com/gregversteeg/linearcorex"
    """
    metadata = PrimitiveMetadata({
      "schema": "v0",
      "id": "d2d4fefc-0859-3522-91df-7e445f61a69b",
      "version": "v0.2.5",
      "name": "corexcontinuous.corex_continuous.CorexContinuous",
      "description": "Return components/latent factors that explain the most multivariate mutual information in the data under Linear Gaussian model. For comparison, PCA returns components explaining the most variance in the data.",
      "python_path": "d3m.primitives.corex_continuous.CorexContinuous",
      "original_python_path": "corexcontinuous.corex_continuous.CorexContinuous",
      "source": {
          "name": "ISI",
          "contact": "mailto:brekelma@usc.edu",
          "uris": ["https://github.com/brekelma/corexcontinuous.git"]
          },

      "installation": [
        {
          "type":"PIP",
          "package":"corexcontinuous",
          "version":"0.2.5"
        }
        ],
      "algorithm_types": ["EXPECTATION_MAXIMIZATION_ALGORITHM"],
      "primitive_family": "FEATURE_CONSTRUCTION",
      "preconditions": ["NO_MISSING_VALUES", "NO_CATEGORICAL_VALUES"],
      "hyperparams_to_tune": ["n_hidden"]
    })
    #  "effects": [],

    #def __init__(self, n_hidden : Any = None, max_iter : int = 10000, 
    def __init__(self, *, hyperparams : CorexContinuous_Hyperparams, random_seed : int =  0, docker_containers: typing.Dict[str, str] = None) -> None:
        # Additional Corex Parameters set to defaults:  see github.com/gregversteeg/LinearCorex
        
        #tol : float = 1e-5, anneal : bool = True, discourage_overlap : bool = True, gaussianize : str = 'standard',  
        #gpu : bool = False, verbose : bool = False, seed : int = None, **kwargs) -> None:
        
        super().__init__(hyperparams = hyperparams, random_seed = random_seed, docker_containers = docker_containers)
        


    def fit(self, *, timeout: float = None, iterations : int = None) -> CallResult[None]:
        if self.fitted:
            return
        if not hasattr(self, 'training_inputs'):
            raise ValueError("Missing training data.")

        self._fit_transform(self.training_inputs, timeout, iterations)
        self.fitted = True
        # add support for max_iter / incomplete
        return CallResult(None, True, self.max_iter)

    def produce(self, *, inputs : Input, timeout : float = None, iterations : int = None) -> CallResult[Output]: 

        self.columns = list(inputs)
        X_ = inputs[self.columns].values 
    	
        if iterations is not None:
            self.max_iter = iterations
        else:
            self.max_iter = 10000

        if not self.fitted:
            raise ValueError('Please fit before calling produce')

        self.latent_factors = self.model.transform(X_)

        return CallResult(self.latent_factors, True, self.max_iter)

    def _fit_transform(self, inputs : Input, timeout: float = None, iterations : int = None) -> Sequence[Output]:
        
        self.columns = list(inputs)
        X_ = inputs[self.columns].values

        if iterations is not None:
            self.max_iter = iterations
        else:
            self.max_iter = 10000

        if isinstance(self.hyperparams['n_hidden'], int):
            self.n_hidden = self.hyperparams['n_hidden']
        elif isinstance(self.hyperparams['n_hidden'], float):
            self.n_hidden = max(1,int(self.hyperparams['n_hidden']*len(self.columns)))

        if not hasattr(self, 'model') or self.model is None:
            self.model = corex_cont.Corex(n_hidden= self.n_hidden, max_iter = self.max_iter)

        self.latent_factors = self.model.fit_transform(X_)
        self.fitted = True
        return self.latent_factors

    def set_training_data(self, *, inputs : Input) -> None:
        self.training_inputs = inputs
        self.fitted = False

    def get_params(self) -> CorexContinuous_Params:
        return CorexContinuous_Params(model = self.model)

    def set_params(self, *, params: CorexContinuous_Params) -> None:
        self.model = params['model']
        #self.fitted = params.fitted
        #self.training_inputs = params.training_inputs


    def _annotation(self):
        if self._annotation is not None:
            return self._annotation
        self._annotation = Primitive()
        self._annotation.name = 'CorexContinuous'
        self._annotation.task = 'FeatureExtraction'
        self._annotation.learning_type = 'UnsupervisedLearning'
        self._annotation.ml_algorithm = ['Dimension Reduction']
        self._annotation.tags = ['feature_extraction', 'continuous']
        return self._annotation

    def _get_feature_names(self):
    	return ['CorexContinuous_'+ str(i) for i in range(self.hyperparams['n_hidden'])]

