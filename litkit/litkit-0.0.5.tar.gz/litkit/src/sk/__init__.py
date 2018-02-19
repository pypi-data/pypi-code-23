import datetime

from sklearn.base import ClassifierMixin, RegressorMixin, ClusterMixin, BiclusterMixin, DensityMixin, MetaEstimatorMixin, TransformerMixin
from sklearn.utils.testing import all_estimators
import pandas as pd


def __get_estimators_df():
    estimators = all_estimators()

    es = {}
    es['name'] = []
    es['classifier'] = []
    es['regressor'] = []
    es['cluster'] = []
    es['bicluster'] = []
    es['density'] = []
    es['meta'] = []
    es['transformer'] = []
    for e in estimators:
        es['name'].append(e[0])
        es['classifier'].append('x' if isinstance(e[1](), ClassifierMixin) else '')
        es['regressor'].append('x' if isinstance(e[1](), RegressorMixin) else '')
        es['cluster'].append('x' if isinstance(e[1](), ClusterMixin) else '')
        es['bicluster'].append('x' if isinstance(e[1](), BiclusterMixin) else '')
        es['density'].append('x' if isinstance(e[1](), DensityMixin) else '')
        es['meta'].append('x' if isinstance(e[1](), MetaEstimatorMixin) else '')
        es['transformer'].append('x' if isinstance(e[1](), TransformerMixin) else '')

    df = pd.DataFrame(es)
    return df[['name', 'meta', 'classifier', 'regressor', 'density', 'transformer', 'cluster', 'bicluster']]


def list_estimators():
    print()
    print(__get_estimators_df())


def list_regressors():
    df = __get_estimators_df()

    print(df[df['regressor'] == 'x'])


def save_cv_results(cv_results):
    r_df = pd.DataFrame(cv_results)
    r_df.to_csv('/tmp/cv_results_{}.cvs'.format(datetime.datetime.now()))
