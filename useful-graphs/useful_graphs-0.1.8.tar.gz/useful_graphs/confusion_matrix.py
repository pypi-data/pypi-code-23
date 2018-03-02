# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import itertools
import math


class ConfusionMatrix:
    """
    Plot confusion matrix.

    Examples
    --------
    >>> import numpy as np
    >>> cm = np.array([
                        [10, 3, 4],
                        [0, 9, 2],
                        [3, 2, 10],
                    ])
    >>> classes = ['test1', 'test2', 'test3']
    >>> myCM = ConfusionMat()
    >>> myCM.read_cm(cm, class_list=classes)
    >>> myCM.plot(to_normalize=True)
    """
    # define constant
    THRESHOLD = 0.5

    def __init__(self):
        self._cm = None

    @property
    def cm(self):
        return None

    @cm.getter
    def cm(self):
        return self._cm

    def read_cm(self, cm, class_list=None):
        """
        Reads from confusion matrix.

        Parameters
        ----------
        cm: a 2-dimensional numpy array
            A confusion matrix which either of columns or rows are true labels, and the other ones are predicted labels.
            I recommend you to use confusion_matrix method in scikit-learn.
        class_list: list, optional
            A list of label names.
            If not specified, range(len(cm)) will be used for labels.

        """

        self._cm = cm
        if class_list==None:
            self.classes = range(len(cm))
        elif class_list:
            self.classes = class_list

    def _normalize_cm(self, cm):
        sums = cm.sum(axis=1)[:, np.newaxis]
        return cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100

    def plot(self,
                    to_normalize=False,
                    title=None,
                    to_show_colorbar=True,
                    cmap=plt.cm.Reds,
                    save_path=None,
                    xlabel='Predicted label',
                    ylabel='True label',
                    text_font_size=10,
                    figsize=None):
        """
        Plot confusion matrix.

        Parameters
        ----------
        to_normalize: bool, optional
        """

        # normalize if to_normalize is True
        if to_normalize:
            cm = self._normalize_cm(self._cm)
        else:
            cm = self._cm

        # set figuresize if specified
        if figsize:
            plt.figure(figsize=figsize)

        plt.imshow(cm, interpolation='nearest', cmap=cmap)

        # set color range when to_normalize is True
        if to_normalize:
            plt.clim(0,100)

        if title:
            plt.title(title, fontsize=15)
        if to_show_colorbar:
            plt.colorbar()

        labels = np.arange(len(self.classes))
        plt.xticks(labels, self.classes, rotation=45)
        plt.yticks(labels, self.classes)

        plt.xlabel(xlabel, fontsize=13)
        plt.ylabel(ylabel, fontsize=13)

        max_of_cm = cm.max()

        for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
            if not math.isnan(cm[i, j]):
                if to_normalize:
                    string = '%.1f%%\n(%d)' % ( cm[i, j], self._cm[i, j] )
                else:
                    string = '%d' % cm[i, j]

                # get color of this cell
                cell_color = cmap(cm[i, j]/max_of_cm)
                rgb_array = [cell_color[0], cell_color[1], cell_color[2]]
                # calculate luminance
                # Reference: https://en.wikipedia.org/wiki/Relative_luminance
                luminance = 0.298912 * rgb_array[0] + 0.586611 * rgb_array[1] + 0.114478 * rgb_array[2]

                # set font color
                if luminance < self.THRESHOLD:
                    color = 'white'
                else:
                    color = 'black'

                plt.text(j, i, string,
                         horizontalalignment="center",
                         verticalalignment="center",
                         color=color,
                         fontsize=text_font_size)

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()


if __name__ == '__main__':
    # cm = np.array([[4, 5, 9, 7, 0, 0], [5, 22, 43, 24, 0, 0], [9, 35, 133, 137, 10, 0], [6, 40, 212, 209, 4, 0], [2, 10, 24, 47, 3, 0], [1, 20, 20, 50, 30, 80]])
    cm = np.array([
                     [4, 5, 9, 7, 0, 0],
                     [5, 22, 43, 24, 0, 0],
                     [9, 35, 133, 137, 10, 0],
                     [6, 40, 212, 209, 4, 0],
                     [2, 10, 24, 47, 3, 0],
                     [1, 20, 20, 50, 30, 80]
                 ])

    classes = ['label1', 'label2', 'label3', 'label4', 'label5', 'label6']
    plot_cm = ConfusionMatrix()
    plot_cm.read_cm(cm, class_list=classes)
    plot_cm.plot(to_normalize=True)
    print(plot_cm.cm)
