import os

import matplotlib
from keras.callbacks import Callback

matplotlib.use('Agg')
import matplotlib.pyplot as plt


class VisualizeHistory(Callback):
    def __init__(self, dir_path):
        super(VisualizeHistory, self).__init__()

        self.dir_path = dir_path

    def on_train_begin(self, logs={}):
        self.epoch = []
        self.history = {}

    def on_epoch_end(self, epoch, logs={}):
        self.epoch.append(epoch)
        for k, v in logs.items():
            self.history.setdefault(k, []).append(v)

        for key in filter(lambda k: not k.startswith('val_'), self.history.keys()):
            val_key = 'val_{}'.format(key)

            plt.figure(figsize=(15, 5))

            plt.plot(self.history[key], label='Train', linewidth=3.0)
            if val_key in self.history:
                plt.plot(self.history[val_key], label='Valid', linewidth=3.0)

            plt.legend()
            plt.ylabel(key)
            plt.xlabel('epoch')

            plt.savefig(os.path.join(self.dir_path, '{}.png'.format(key)))
            plt.close()
