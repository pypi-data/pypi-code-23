"""
nosetests -sv --nologcapture tests/quick_test.py
nosetests --verbosity=2 --detailed-errors --nologcapture --processes=4 --process-restartworker --process-timeout=1000 tests/quick_test.py
"""

import datetime
import os
import random
import sys
sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path
os.environ['is_test_suite'] = 'True'
# os.environ['KERAS_BACKEND'] = 'theano'

from auto_ml import Predictor
from auto_ml.utils_models import load_ml_model

from sklearn.metrics import accuracy_score

import dill
import numpy as np
import pandas as pd
from sklearn.datasets import load_boston
from sklearn.metrics import brier_score_loss, mean_squared_error
from sklearn.model_selection import train_test_split


def get_boston_regression_dataset():
    boston = load_boston()
    df_boston = pd.DataFrame(boston.data)
    df_boston.columns = boston.feature_names
    df_boston['MEDV'] = boston['target']
    df_boston_train, df_boston_test = train_test_split(df_boston, test_size=0.33, random_state=42)
    return df_boston_train, df_boston_test


def calculate_brier_score_loss(actuals, probas):
    return -1 * brier_score_loss(actuals, probas)


def regression_test():
    # a random seed of 42 has ExtraTreesRegressor getting the best CV score, and that model doesn't generalize as well as GradientBoostingRegressor.
    np.random.seed(0)
    model_name = 'LGBMRegressor'

    df_boston_train, df_boston_test = get_boston_regression_dataset()
    many_dfs = []
    for i in range(10):
        many_dfs.append(df_boston_train)
    df_boston_train = pd.concat(many_dfs)


    column_descriptions = {
        'MEDV': 'output'
        , 'CHAS': 'categorical'
    }

    ml_predictor = Predictor(type_of_estimator='regressor', column_descriptions=column_descriptions)

    ml_predictor.train(df_boston_train, model_names=[model_name], perform_feature_scaling=False)

    test_score = ml_predictor.score(df_boston_test, df_boston_test.MEDV)

    print('test_score')
    print(test_score)

    lower_bound = -3.2
    if model_name == 'DeepLearningRegressor':
        lower_bound = -7.8
    if model_name == 'LGBMRegressor':
        lower_bound = -3.5
    if model_name == 'XGBRegressor':
        lower_bound = -3.4

    assert lower_bound < test_score < -2.8


def get_titanic_binary_classification_dataset(basic=True):
    try:
        df_titanic = pd.read_csv(os.path.join('tests', 'titanic.csv'))
    except Exception as e:
        print('Error')
        print(e)
        dataset_url = 'http://biostat.mc.vanderbilt.edu/wiki/pub/Main/DataSets/titanic3.csv'
        df_titanic = pd.read_csv(dataset_url)
        # Do not write the index that pandas automatically creates
        df_titanic.to_csv(os.path.join('tests', 'titanic.csv'), index=False)

    df_titanic = df_titanic.drop(['boat', 'body'], axis=1)

    if basic == True:
        df_titanic = df_titanic.drop(['name', 'ticket', 'cabin', 'home.dest'], axis=1)

    df_titanic_train, df_titanic_test = train_test_split(df_titanic, test_size=0.33, random_state=42)
    return df_titanic_train, df_titanic_test


def classification_test():
    np.random.seed(0)
    model_name = 'LGBMClassifier'

    df_titanic_train, df_titanic_test = get_titanic_binary_classification_dataset()

    column_descriptions = {
        'survived': 'output'
        , 'embarked': 'categorical'
        , 'pclass': 'categorical'
        , 'sex': 'categorical'
    }

    ml_predictor = Predictor(type_of_estimator='classifier', column_descriptions=column_descriptions)

    ml_predictor.train(df_titanic_train, model_names=model_name)

    test_score = ml_predictor.score(df_titanic_test, df_titanic_test.survived)

    print('test_score')
    print(test_score)

    lower_bound = -0.16
    if model_name == 'DeepLearningClassifier':
        lower_bound = -0.245
    if model_name == 'LGBMClassifier':
        lower_bound = -0.225

    assert lower_bound < test_score < -0.135

    file_name = ml_predictor.save(str(random.random()))

    saved_ml_pipeline = load_ml_model(file_name)

    os.remove(file_name)
    try:
        keras_file_name = file_name[:-5] + '_keras_deep_learning_model.h5'
        os.remove(keras_file_name)
    except:
        pass


    df_titanic_test_dictionaries = df_titanic_test.to_dict('records')

    # 1. make sure the accuracy is the same

    predictions = []
    for row in df_titanic_test_dictionaries:
        predictions.append(saved_ml_pipeline.predict_proba(row)[1])


    first_score = calculate_brier_score_loss(df_titanic_test.survived, predictions)
    print('first_score')
    print(first_score)
    # Make sure our score is good, but not unreasonably good

    lower_bound = -0.16

    assert -0.16 < first_score < -0.135

    # 2. make sure the speed is reasonable (do it a few extra times)
    data_length = len(df_titanic_test_dictionaries)
    start_time = datetime.datetime.now()
    for idx in range(1000):
        row_num = idx % data_length
        saved_ml_pipeline.predict(df_titanic_test_dictionaries[row_num])
    end_time = datetime.datetime.now()
    duration = end_time - start_time

    print('duration.total_seconds()')
    print(duration.total_seconds())

    # It's very difficult to set a benchmark for speed that will work across all machines.
    # On my 2013 bottom of the line 15" MacBook Pro, this runs in about 0.8 seconds for 1000 predictions
    # That's about 1 millisecond per prediction
    # Assuming we might be running on a test box that's pretty weak, multiply by 3
    # Also make sure we're not running unreasonably quickly
    assert 0.2 < duration.total_seconds() < 15


    # 3. make sure we're not modifying the dictionaries (the score is the same after running a few experiments as it is the first time)

    predictions = []
    for row in df_titanic_test_dictionaries:
        predictions.append(saved_ml_pipeline.predict_proba(row)[1])

    second_score = calculate_brier_score_loss(df_titanic_test.survived, predictions)
    print('second_score')
    print(second_score)
    # Make sure our score is good, but not unreasonably good

    assert -0.16 < second_score < -0.135



if __name__ == '__main__':
    classification_test()
