"""
Tools for pandas
Copyright (C) 2017 - Pietro Mascolo

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Author: Pietro Mascolo
Email: iz4vve@gmail.com
"""
import numpy as np
import pandas as pd
import progressbar


def load_files(paths, func=pd.read_csv, *args, **kwargs):
    """
    Loads files in paths, concatenates them and returns a dataframe
    Assumes all files have the same structure
    :param paths: list of file paths
    :return: dataframe of all data
    """
    df = pd.DataFrame()
    _bar = progressbar.ProgressBar(max_value=len(paths))
    for n, path in enumerate(paths):
        _bar.update(n + 1)
        if not n:
            df = func(path, *args, **kwargs)
            continue
        df = pd.concat([df, func(path, *args, **kwargs)], axis=0)

    return df


def find_correlated(df, threshold=0.8, **kwargs):
    """
    Finds fields in a df with a correlation coefficient higher than threshold
    (or lower than -threshold)
    """
    corrs = df.corr(**kwargs)#.stack()
    corrs = corrs.where(np.triu(np.ones(corrs.shape)).astype(np.bool)).stack()
    return (corr for corr in corrs.items() if threshold < abs(corr[1]) < 1)