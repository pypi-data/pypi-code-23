"""
Tools for plotting (matplotlib, ...)
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
import itertools
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap


optum_cmap = LinearSegmentedColormap.from_list(
    'optum', ["#E87722", "#A32A2E", "#422C88", "#078576", "#627D32"]
)
optum_cmap_simple = LinearSegmentedColormap.from_list(
    'optum', ["#E87722", "#078576"]
)  # for gradients


def rand_jitter(arr, scatter=0.1):
    stdev = scatter*(max(arr)-min(arr))
    return arr + np.random.randn(len(arr)) * stdev


def jitter(x, y, s=20, c='b', marker='o',
           cmap=None, norm=None, vmin=None, vmax=None, alpha=None,
           linewidths=None, verts=None, hold=None, scatter=0.1, **kwargs):
    return plt.scatter(
        rand_jitter(x, scatter=scatter),
        rand_jitter(y, scatter=scatter),
        s=s, c=c, marker=marker, cmap=cmap,
        norm=norm, vmin=vmin, vmax=vmax, alpha=alpha,
        linewidths=linewidths, verts=verts, hold=hold, **kwargs
    )


def plot_confusion_matrix(cm, classes,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    cm1 = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f'
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, f"{cm[i, j]:.2f}\n{cm1[i, j]:.2%}",
                 horizontalalignment="center",
                 color="white" if cm1[i, j] > 0.5 else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')


def plot_correlations(df, T, cmap=None):
    """
    This functions plots the correlations in a dataset above a given threshold

    :param df: dataset on which to calculate correlations
    :param T: Threshold of correlations to show
    :param cmap: color map for visualization. Default uses two colours from Optum palette
    :type cmap: matplotlib.color.LinearSegmentedColormap
    """

    if cmap is None:
        cmap = LinearSegmentedColormap.from_list('optum', ["#E87722", "#078576"])

    c = df.corr()
    c = c.where(np.triu(np.ones(c.shape)).astype(np.bool))  # filter tril
    c = c.where((abs(c) > T)).where(c != 1)  # filter diag

    # get column/row names of interesting corrs
    cols = [(n, col) for n, col in enumerate(c.columns) if any(abs(i) > T for i in c[col])]
    indices, cols = list(zip(*cols))

    row_cols = [(n, row) for n, row in enumerate(c.index) if any(abs(i) > T for i in c.loc[row, :])]
    row_indices, rows = list(zip(*row_cols))

    plt.imshow(c, cmap=cmap)
    plt.xticks(indices, cols, rotation="vertical")
    plt.yticks(row_indices, rows)

    plt.colorbar()
    plt.title(f"High correlations map: Threshold={T}")
    plt.show()