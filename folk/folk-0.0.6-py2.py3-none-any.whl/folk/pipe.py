"""Parameterized pipeline abstraction."""


class ParameterizedPipeline(object):
    """A parameterized pipeline.

    This class was written with pdpipe.Pipeline objects in mind, but can be
    used with all callables that transform pandas.DataFrame objects.

    Parameters
    ----------
    pipeline_getter : function
        A function that returns a pipeline for pandas DataFrame objects when
        supplied with values for its required keyword arguments, ignoring any
        unkown keyword arguments.
    param_grid : iterable over dict of string to any
        An iterable over parameter realizations. The ParameterGrid sklearn
        class is a great example.
    """

    def __init__(self, pipeline_getter, param_grid):
        self.pipeline_getter = pipeline_getter
        self.param_grid = param_grid

    def __iter__(self):
        """Iterate over all pipelines induced by this parameterized pipeline.

        Returns
        -------
        models : iterator over callable objects
            Yields callable objects that can be applied to dataframe objects
            to produce new dataframes.
        """
        for params in self.param_grid:
            yield self.pipeline_getter(**params)

    def pipe_n_params_iter(self):
        """Iterate on all pipeline and parameters pairs induced by this
        parameterized pipieline.

        Returns
        -------
        models : iterator over tuples
            Yields 2-tuples of a pdpipe.Pipeline and a dict.
        """
        for params in self.param_grid:
            yield self.pipeline_getter(**params), params

    def pipeline_by_params(self, params):
        """Returns a realized pipeline by the given params.

        Parameters
        ----------
        params : dict of string to any
            Parameter assignments by which to produce a pipeline.

        Returns
        -------
        callable
            A callable object that can be applied to dataframe objects
            to produce new dataframes.
        """
        return self.pipeline_getter(**params)
