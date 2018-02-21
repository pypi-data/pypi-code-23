from sklearn.linear_model import Lasso, LinearRegression, ElasticNet, Ridge
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
import pandas as pd

from litkit.src.dash.viewer import view
from litkit.src.data import get_baseball_df


p = Pipeline([
    ('estimator', Lasso())
])

pg = [
    {'estimator': [Lasso(), LinearRegression(), ElasticNet(), Ridge()]}
]

gs = GridSearchCV(estimator=p, param_grid=pg, verbose=2, n_jobs=1, return_train_score=True)

df = get_baseball_df()

y = df['RS']
X = df[['RA', 'W', 'OBP', 'SLG']]

gs.fit(X, y)

r_df = pd.DataFrame(gs.cv_results_)

del r_df['params']
r_df['param_estimator'] = r_df['param_estimator'].apply(lambda x: x.__class__.__name__)

view(r_df)