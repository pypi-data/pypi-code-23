from abc import abstractmethod
from collections import defaultdict
from operator import itemgetter

import pathos.pools as pp
import six
from six.moves import map
from sklearn.base import BaseEstimator
from tqdm import tqdm

from .errors import has_step_error


class Step(BaseEstimator):
    GIVE_ALL = False

    @abstractmethod
    def transform(self, params):
        """
        Parameters
        ----------
        params : dict|list
            If GIVE_ALL is False, then param will be dict. It contains all information returned by previous
            steps.
            If GIVE_ALL is True, then param will be list. It contains a dicts that contains all information about all
            examples given to pipeline.

        Returns
        -------
        dict|list|None
            Should return dict or list that contains informations that will be helpful in the consecutive steps
            in a pipeline. Can return None, if you do now pass and informations.

        """
        pass

    def fit_transform(self, params):
        return self.transform(params)


class Pipeline(Step):
    """
    Parameters
    ----------
    show_progressbar : bool, optional
        Flag that indicates if progressbar should be shown.
    parallel : bool, optional
        If parallel is True, then all examples will run in parallel. Default: False.
    """

    def __init__(self, *steps, **kwargs):
        self.show_progressbar = kwargs.get('show_progressbar', True)
        self.parallel = kwargs.get('parallel', False)
        self.parallel_processes = kwargs.get('parallel_processes', 4)
        self.steps = steps

    def transform(self, params, f='transform'):
        was_single = False

        if isinstance(params, dict):
            params = [params]
            was_single = True

        result = self._transform_single(params, f)

        if was_single:
            return result[0]

        return result

    def fit_transform(self, params):
        return self.transform(params, f='fit_transform')

    def _transform_single(self, rows, f):
        for name, step in self.steps:
            func = getattr(step, f)

            aa = [(i, row) for i, row in enumerate(rows) if has_step_error(row)]
            indices = map(itemgetter(0), aa)
            for index in sorted(indices, reverse=True):
                del rows[index]

            if step.GIVE_ALL:
                new_rows = func(rows)

                if isinstance(new_rows, list):
                    rows = new_rows
            else:
                if self.parallel:
                    mapper = pp.ProcessPool(self.parallel_processes).imap
                else:
                    mapper = map

                mapper = mapper(func, rows)

                if self.show_progressbar:
                    progressbar = tqdm(mapper, total=len(rows), desc=name)
                else:
                    progressbar = mapper

                new_rows = list(progressbar)

                for n, o in zip(new_rows, rows):
                    if isinstance(n, dict):
                        if isinstance(step, Pipeline):
                            n = {"{}_{}".format(name, k):v for k, v in six.iteritems(n)}
                        o.update(n)

            for index, row in sorted(aa, reverse=False, key=itemgetter(0)):
                rows.insert(index, row)

        return rows

    def set_params(self, **params):
        parameters_to_set = defaultdict(dict)
        for k, v in six.iteritems(params):
            transformer, param = k.split('__', 1)
            parameters_to_set[transformer][param] = v

        for name, transformer in self.steps:
            transformer.set_params(**parameters_to_set[name])

    def get_params(self, *args, **kwargs):
        output = {}

        for name, transformer in self.steps:
            for p, v in six.iteritems(transformer.get_params()):
                if isinstance(v, Pipeline):
                    continue

                output['{}__{}'.format(name, p)] = v

        return output
