class Illustration(Callback):
    """
    Samples a random image from the batch.

    Parameters:
    ----------
    Data Entity: the class of the data entity
    """

    def __init__(self, de, n=1):
        self.de = de
        self.n = n
    
    def on_batch_end(self, batch, logs=None):
        self.most_recent_batch = batch

    def on_epoch_end(self, epoch, logs=None):
        ##### To-Do: Give callbacks access to original data entity!
        if self.epoch % self.n == 0:
            self.de.
 