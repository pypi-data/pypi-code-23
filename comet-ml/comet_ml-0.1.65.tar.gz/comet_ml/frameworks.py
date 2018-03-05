'''
Extends keras Callbacks. Provides automatic logging and tracking with Comet.ml
'''

from keras.callbacks import Callback


class EmptyKerasCallback(Callback):
    """
    Empty Keras callback. TODO(gidim): remove this
    """

    def __init__(self):
        super(EmptyKerasCallback, self).__init__()

    def on_epoch_begin(self, epoch, logs=None):
        pass

    def on_epoch_end(self, epoch, logs=None):
        pass

    def on_batch_begin(self, batch, logs=None):
        pass

    def on_batch_end(self, batch, logs=None):
        pass

    def on_train_begin(self, logs=None):
        pass


class KerasCallback(Callback):
    """ Keras callback to report params, metrics to Comet.ml Experiemnt()"""

    def __init__(self, experiment, log_params=True, log_metrics=True):
        '''
        Create a new experiment and submit source code.
        :param api_key: User's API key. Required.
        '''
        super(KerasCallback, self).__init__()

        # Inits the experiment with reference to the name of this class. Required for loading the correct
        # script file
        self.experiment = experiment
        self.log_params = log_params
        self.log_metrics = log_metrics
        self.our_step = 0

    def on_epoch_begin(self, epoch, logs=None):
        pass

    def on_epoch_end(self, epoch, logs=None):
        if self.log_metrics:
            self.experiment.log_epoch_end(epoch, step=self.our_step)
            if logs:
                for name, val in logs.items():
                    self.experiment.log_metric(name, val, step=self.our_step)

    def on_batch_begin(self, batch, logs=None):
        pass

    def on_batch_end(self, batch, logs=None):
        '''
        Logs training metrics.
        '''

        self.our_step += 1

        if logs and self.log_metrics:
            for name, val in logs.items():
                self.experiment.log_metric(name, val, step=self.our_step)

    def on_train_begin(self, logs=None):
        '''
        Sets model graph.
        '''
        self.experiment.set_model_graph(self.model.to_json())

        if self.log_params:
            if logs:
                for k, v in logs.items():
                    self.experiment.log_parameter(k, v)

            # Keras Callback doesn't set this parameter at creation by default
            if hasattr(self, 'params') and self.params:
                for k, v in self.params.items():
                    if k != 'metrics':
                        self.experiment.log_parameter(k, v)
