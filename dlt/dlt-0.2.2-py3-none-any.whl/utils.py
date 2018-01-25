"""
Common tools
"""

import itertools
import os
from statistics import mean, median, variance, stdev

import matplotlib as mpl

if os.environ.get('DISPLAY', '') == '':
    print('no display found. Using non-interactive Agg backend')
    mpl.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix


class Dataset():
    """Simple dataset container
    """

    def __init__(self, **kwds):
        """Summary

        Args:
            **kwds:
        """
        self.__dict__.update(kwds)

    def plot_examples(self, num_examples=5, fname=None):
        """Plot examples from the dataset

        Args:
            num_examples (int, optional): number of examples to
            fname (str, optional): filename for saving the plot
        """
        plot_examples(self, num_examples, fname)


def plot_image(x, ax=None):
    """Plot an image X.

    Args:
        x (2D array): image, grayscale or RGB
        ax (None, optional): Description
    """
    if ax is None:
        ax = plt.gca()

    if (x.ndim == 2) or (x.shape[-1] == 1):
        ax.imshow(x.astype('uint8'), origin='upper', cmap=plt.cm.Greys)
    else:
        ax.imshow(x.astype('uint8'), origin='upper')

    ax.set(xticks=[], yticks=[])


def plot_examples(data, num_examples=5, fname=None):
    """Plot the first examples for each class in given Dataset.

    Args:
        data (Dataset): a dataset
        num_examples (int, optional): number of examples to plot for each class
        fname (str, optional): filename for saving the plot
    """

    n = len(data.classes)
    fig, axes = plt.subplots(num_examples, n, figsize=(n, num_examples))

    for l in range(n):
        axes[0, l].set_title(data.classes[l], fontsize='smaller')
        images = data.train_images[np.where(data.train_labels == l)[0]]
        for i in range(num_examples):
            plot_image(images[i], axes[i, l])

    save_fig(fig, fname)


def plot_prediction(Yp, X, y, classes=None, top_n=False, fname=None):
    """Plot an image along with all or the top_n predictions.

    Args:
        Yp (1D array): predicted probabilities for each class
        X (2D array): image
        y (integer): true class label
        classes (1D array, optional): class names
        top_n (int, optional): number of top predictions to show
        fname (str, optional): filename for saving the plot
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6, 3.2))
    plt.subplots_adjust(left=0.02, right=0.98,
                        bottom=0.15, top=0.98, wspace=0.02)
    plot_image(X, ax1)

    if top_n:
        n = top_n
        s = np.argsort(Yp)[-top_n:]
    else:
        n = len(Yp)
        s = np.arange(n)[::-1]

    patches = ax2.barh(np.arange(n), Yp[s], align='center')
    ax2.set(xlim=(0, 1), xlabel='Probability', yticks=[])

    for iy, patch in zip(s, patches):
        if iy == y:
            patch.set_facecolor('C1')  # color correct patch

    if classes is None:
        classes = np.arange(0, np.size(Yp))

    for i in range(n):
        ax2.text(0.05, i, classes[s][i], ha='left', va='center')

    save_fig(fig, fname)


def plot_distribution_data(Y, dataset_name, classes, fname=None):
    """Plot the distribution of dataset and show the statistics information

    :param Y: target data for X_train or X_test
    :param data_type (str): set the name of Y
    :param classes (1D array, optional): class names
    :param fname: filename
    :return: image file
    """
    fig, ax = plt.subplots(figsize=(10, 4))

    num = []
    n = len(classes)
    for i in range(n):
        num.append(len(np.where(Y == i)[0]))

    print("Mean Value: {0}".format(round(mean(num), 2)))
    print("Median Value: {0}".format(round(median(num), 2)))
    print("Variance: {0}".format(round(variance(num), 2)))
    print("Standard Deviation: {0}".format(round(stdev(num), 2)))

    ax.bar(np.arange(n), num, tick_label=classes, label=dataset_name)
    for x, y in zip(classes, num):
        ax.text(np.where(x == classes)[0], y, y, ha='center', va='bottom')
    fig.suptitle("Distribution of data for each label")
    ax.set_xlabel("Categories / Labels")
    ax.set_ylabel("Number of entries")
    ax.set_ylim(ymin=mean(num) / 2)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)

    save_fig(fig, fname)


def plot_confusion_matrix(test_labels, y_pred, classes,
                          title='Confusion matrix',
                          fname=None):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.

    The original code was developed by scikit-learn.
    """
    cm = confusion_matrix(test_labels, y_pred)
    cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100

    fig = plt.figure(figsize=(9, 9))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.YlGnBu)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], '.2f'),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    # plt.tight_layout()
    plt.ylabel('True label (%)')
    plt.xlabel('Predicted label (%)')

    save_fig(fig, fname)


def plot_loss_and_accuracy(fit, fname=None):
    """Plot loss function value and accuracy graph

    Args:
        fit: instance of model.fit)
        fname: output path
    return: loss and accuracy plot graph
    """
    fig, (axL, axR) = plt.subplots(ncols=2, figsize=(10, 4))

    # Plot the loss in the history
    axL.plot(fit.history['loss'], label="loss for training")
    if fit.history['val_loss'] is not None:
        axL.plot(fit.history['val_loss'], label="loss for validation")
    axL.set_title('model loss')
    axL.set_xlabel('epoch')
    axL.set_ylabel('loss')
    axL.legend(loc='upper right')

    # Plot the loss in the history
    axR.plot(fit.history['acc'], label="loss for training")
    if fit.history['val_acc'] is not None:
        axR.plot(fit.history['val_acc'], label="loss for validation")
    axR.set_title('model accuracy')
    axR.set_xlabel('epoch')
    axR.set_ylabel('accuracy')
    axR.legend(loc='lower right')

    save_fig(fig, fname)


def save_fig(fig, fname=None):
    if fname is not None:
        fig.savefig(fname, bbox_inches='tight')
    plt.close()


def __main():
    """Test code on Travis.CI"""
    from keras.layers import Conv2D, Dense, Dropout, MaxPooling2D, Flatten
    from keras.losses import categorical_crossentropy
    from keras.models import Sequential
    from keras.optimizers import Adadelta
    from keras.utils.np_utils import to_categorical
    import dlt

    # ---------------------------------------------------------
    # Load and preprocess data
    # ---------------------------------------------------------
    data = dlt.fashion_mnist.load_data()

    # plot some example images
    dlt.utils.plot_examples(data, fname='examples.png')

    # preprocess the data in a suitable way
    # reshape the image matrices to vectors
    # RGB 255 = white, 0 = black
    X_train = data.train_images.reshape([-1, 28, 28, 1])
    X_test = data.test_images.reshape([-1, 28, 28, 1])

    # convert integer RGB values (0-255) to float values (0-1)
    X_train = X_train.astype('float32') / 255
    X_test = X_test.astype('float32') / 255

    # convert class labels to one-hot encodings
    Y_train = to_categorical(data.train_labels, 10)
    Y_test = to_categorical(data.test_labels, 10)

    # Plot data distribution for Y_train
    dlt.utils.plot_distribution_data(Y=data.train_labels,
                                     dataset_name='Y_train',
                                     classes=data.classes,
                                     fname='dist_train.png')
    # ----------------------------------------------------------
    # Model and training
    # ----------------------------------------------------------

    model = Sequential()
    model.add(Conv2D(32, kernel_size=(3, 3),
                     activation='relu',
                     input_shape=(28, 28, 1)))
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(10, activation='softmax'))

    model.compile(loss=categorical_crossentropy,
                  optimizer=Adadelta(),
                  metrics=['accuracy'])

    fit = model.fit(X_train, Y_train,
                    batch_size=128,
                    epochs=3,
                    verbose=1,
                    validation_data=(X_test, Y_test))

    score = model.evaluate(X_test, Y_test,
                           verbose=0
                           )
    print('Test score:', score[0])
    print('Test accuracy:', score[1])

    # ----------------------------------------------
    # Some plots
    # ----------------------------------------------

    # model.save(os.path.join(folder, 'my_model.h5'))

    # predicted probabilities for the test set
    Yp = model.predict(X_test)
    yp = np.argmax(Yp, axis=1)

    # plot some test images along with the prediction
    for i in range(10):
        dlt.utils.plot_prediction(
            Yp[i],
            data.test_images[i],
            data.test_labels[i],
            data.classes,
            fname='test-%i.png' % i)

    # plot the confusion matrix
    dlt.utils.plot_confusion_matrix(data.test_labels, yp, data.classes,
                                    title='confusion matrix',
                                    fname='confusion matrix.png')

    # plot the loss and accuracy graph
    dlt.utils.plot_loss_and_accuracy(fit,  # model.fitのインスタンス
                                     fname='loss_and_accuracy_graph.png'  # 保存するファイル名とパス
                                     )


if __name__ == '__main__':
    __main()
