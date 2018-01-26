# -*- coding: utf-8 -*-

import pandas

x = pandas.DataFrame({
    'x_1': [0, 1, 2, 3, ],
    'x_2': [0, 1, 2, 3, ],
    'x_3': [0, 1, 2, 3, ],
    'x_4': [0, 1, 2, 3, ], },
    index=[0, 1, 2, 3])

y = pandas.DataFrame({
    'y_1': [0, 1, 2, 3, ],
    'y_2': [0, 1, 2, 3, ], },
    index=[0, 1, 2, 3])

x_str = pandas.DataFrame({
    'x_1': [0, 1, 2, 3, ],
    'x_2': [0, 1, 2, 3, ],
    'x_3': [0, 1, 2, 3, ],
    'x_4': [0, 1, 2, 3, ],
    'x_5': ['a', 'b', 'a', 'a', ], },
    index=[0, 1, 2, 3])

y_str = pandas.DataFrame({
    'y_1': [0, 1, 2, 3, ],
    'y_2': [0, 1, 2, 3, ],
    'y_3': ['a', 'a', 'a', 'b', ], },
    index=[0, 1, 2, 3])

x_nan = pandas.DataFrame({
    'x_1': [0, 1, 2, 3, 0, 1, 2, None, ],
    'x_2': [0, 1, 2, 3, 0, 1, 2, pandas.np.nan, ],
    'x_3': [0, 1, 2, 3, 0, 1, 2, None, ],
    'x_4': [0, 1, 2, 3, 0, pandas.np.NAN, 2, None, ],
    'x_5': ['a', 'b', 'b', 'a', 'b', None, 'a', 'b'], },
    index=[0, 1, 2, 3, 4, 5, 6, 7])

y_nan = pandas.DataFrame({
    'y_1': [0, None, 2, 3, 0, 1, 2, None, ],
    'y_2': [0, 1, 2, None, 0, 1, 2, None, ], },
    index=[0, 1, 2, 3, 4, 5, 6, 7])
