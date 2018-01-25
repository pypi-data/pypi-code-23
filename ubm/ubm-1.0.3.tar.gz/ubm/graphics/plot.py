from matplotlib import pyplot as plt


class Plot:

    def __init__(self):
        self.plt = plt
        self.plt._default_plot = self.plt.plot
        self.plt.plot = self.plot

    def get(self):
        return self.plt

    def plot(self, *args, **kwargs):
        if 'label' not in kwargs:
            print(globals().items())
            kwargs['label'] = [k for k, v in globals().items() if v is args[0]]
        self.plt._default_plot(*args, **kwargs)
