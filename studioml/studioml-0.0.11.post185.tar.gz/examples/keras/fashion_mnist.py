import sys
import urllib

from keras.layers import Dense, Flatten

from keras.models import Sequential

###
# AS OF 10/18/2017, fashion_mnist available as a part of github master
# branch of keras
# but not a part of pypi package
# Therefore, to use this, you'll need keras installed from a git repo:
# git clone https://github.com/fchollet/keras && cd keras && pip install .
###
from keras.datasets import fashion_mnist
from keras.utils import to_categorical

from keras.callbacks import ModelCheckpoint, TensorBoard
from keras import optimizers

import numpy as np
from PIL import Image
from io import BytesIO

from studio import fs_tracker, model_util

(x_train, y_train), (x_test, y_test) = fashion_mnist.load_data()

x_train = x_train.reshape(60000, 28, 28, 1)
x_test = x_test.reshape(10000, 28, 28, 1)
x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
x_train /= 255
x_test /= 255

# convert class vectors to binary class matrices
y_train = to_categorical(y_train, 10)
y_test = to_categorical(y_test, 10)


model = Sequential()

model.add(Flatten(input_shape=(28, 28, 1)))
model.add(Dense(128, activation='relu'))
model.add(Dense(128, activation='relu'))

model.add(Dense(10, activation='softmax'))
model.summary()


batch_size = 128
no_epochs = int(sys.argv[1]) if len(sys.argv) > 1 else 10
lr = 0.01

print('learning rate = {}'.format(lr))
print('batch size = {}'.format(batch_size))
print('no_epochs = {}'.format(no_epochs))

model.compile(loss='categorical_crossentropy', optimizer=optimizers.SGD(lr=lr),
              metrics=['accuracy'])


checkpointer = ModelCheckpoint(
    fs_tracker.get_model_directory() +
    '/checkpoint.{epoch:02d}-{val_loss:.2f}.hdf')


tbcallback = TensorBoard(log_dir=fs_tracker.get_tensorboard_dir(),
                         histogram_freq=0,
                         write_graph=True,
                         write_images=True)


model.fit(
    x_train, y_train, validation_data=(
        x_test,
        y_test),
    epochs=no_epochs,
    callbacks=[checkpointer, tbcallback],
    batch_size=batch_size)
