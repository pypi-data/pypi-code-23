import shutil
import tempfile
from unittest import TestCase

import numpy as np
from keras.layers.core import Dense, Activation
from keras.models import Sequential
from keras.optimizers import SGD

from rndtools.train import train_model


class Test(TestCase):
    def test_all_good(self):
        def get_model():
            model = Sequential()
            model.add(Dense(8, input_dim=2))
            model.add(Dense(1))
            model.add(Activation('sigmoid'))

            sgd = SGD(lr=0.1)
            model.compile(loss='binary_crossentropy', optimizer=sgd)

            return model

        def train(model, model_dir, data, callbacks):
            return model.fit(data[0], data[1], show_accuracy=True, batch_size=1, nb_epoch=10, callbacks=callbacks)

        def load_data():
            X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
            y = np.array([[0], [1], [1], [0]])

            return X, y

        dirpath = tempfile.mkdtemp()

        train_model(
            dirpath,
            get_model,
            train,
            load_data,
            overwrite=True
        )

        shutil.rmtree(dirpath)
