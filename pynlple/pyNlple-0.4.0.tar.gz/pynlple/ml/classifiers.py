"""
    This module implements custom classifiers of Sklearn's Pipeline
"""
from pynlple.processing.stopwords import FileFolderTokenMapping, DictionaryBasedTagger, DictionaryLookUp
from pynlple.ml.transformers import ToSeries, VocabularyFeature, SubCategoryGenerator, ThresholdRuleVectorClassifier

from sklearn.preprocessing import FunctionTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, ClassifierMixin

import pandas as pd
import numpy as np
from itertools import chain


class LexiconClassifier(BaseEstimator, ClassifierMixin):

    def __init__(self, lexicon_path, rules, stop_rules=list(), overlap_entities=False, class_gramms=(1,3)):
        self.lexicon_path = lexicon_path
        self.default_value = 0
        self.class_value = 1
        self.stop_value = -1
        self.rules = rules
        self.stop_rules = stop_rules
        self.overlap_entities = overlap_entities
        self.class_gramms = class_gramms
        self.join_s = '/'
        self._tagger = DictionaryBasedTagger(DictionaryLookUp(FileFolderTokenMapping([],
                                                                                     data_folder=self.lexicon_path),
                                                              preprocessing_method=str.lower))

        self._to_series = ToSeries()
        self._extractor = VocabularyFeature(self._tagger, self.overlap_entities)
        self._transformer_pipe = Pipeline([
                ('category_extractor', SubCategoryGenerator(self.class_gramms, self.join_s)),
                ('count_vectorizer', CountVectorizer(lowercase=False, analyzer=chain.from_iterable,)),
                ('to_array', FunctionTransformer(func=lambda x: x.toarray(), accept_sparse=True)),
        ])
        self._classifier = ThresholdRuleVectorClassifier(self.default_value)

        stop_classes = np.full((len(self.stop_rules)), self.stop_value)
        classes = np.full((len(self.rules)), self.class_value)
        all_classes = np.hstack((classes, stop_classes))
        all_rules = pd.Series(self.rules).append(pd.Series(self.stop_rules))

        self._transformer_pipe = self._transformer_pipe.fit(all_rules)
        self._classifier = self._classifier.fit(self._transformer_pipe.transform(all_rules), all_classes)

        self.tagger_pipeline = Pipeline([
                ('to_series', self._to_series),
                ('extractor', self._extractor),
                ('transformer', self._transformer_pipe),
                ('classifier', self._classifier),
        ])

    def __check_prediction_array(self, pred):
        return np.all(pred != self.stop_value) and np.any(pred == self.class_value)

    def transform(self, X):
        return self.tagger_pipeline.predict(X)

    def predict(self, X):
        return np.apply_along_axis(lambda x: self.__check_prediction_array(x), axis=1, arr=self.transform(X))