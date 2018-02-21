import os

import pandas as pd
import numpy as np


d = os.path.dirname(os.path.realpath(__file__))


def get_baseball_df():
    df = pd.read_csv(d + '/baseball.csv')

    df = df.replace(['?'], [np.nan])

    return df


def get_cv_results_df():
    df = pd.read_csv(d + '/cv_results.csv')

    return df
