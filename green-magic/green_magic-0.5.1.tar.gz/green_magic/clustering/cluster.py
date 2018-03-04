from collections import Counter
from collections import OrderedDict
import numpy as np
from nltk.util import ngrams as nltk_ngrams
from green_magic.features import enctype2features
from green_magic.utils import extract_value, gen_values, generate_tokens, generate_tokens_with_padding


class Clustering(object):
    """
    An instance of this class encapsulates the behaviour of a clustering; a set of clusters estimated on some data
    """
    def __init__(self, clid2members, active_variables, an_id, map_buffer, value_sets):
        """
        :param clid2members: mapping of cluster numerical ids to sets of strain ids
        :type clid2members: dict
        :param active_variables: the variables taken into account for cl the data
        :type active_variables: tuple
        :param an_id: a unique identifier for the Clustering object
        :type an_id: str
        :param map_buffer: a string that can be directly printed showing the topology of the clusters
        :type map_buffer: str
        """
        self._av = active_variables
        self.clusters = [Cluster(cl_id, clid2members[cl_id], self._av) for cl_id in range(len(clid2members))]
        self.id = an_id
        self.map_buffer = map_buffer
        self.value_sets = value_sets

    @property
    def active_variables(self):
        return self._av

    def __str__(self):
        pre = 2
        body, max_lens = self._get_rows(threshold=10, prob_precision=pre)
        header = self._get_header(max_lens, pre, [_ for _ in range(len(self))])
        return header + body

    def _get_header(self, max_lens, prec, selected_clusters):
        assert len(max_lens) == len(selected_clusters)
        return ' - '.join('id:{} len:{}'.format(cl.id, len(cl)) + ' ' * (prec + max_lens[i] - len(str(len(cl))) - 6) for i, cl in enumerate(self.gen_clusters(selected_clusters))) + '\n'

    def __len__(self):
        return len(self.clusters)

    def __getitem__(self, item):
        return self.clusters[item]

    def gen_ids_and_assigned_clusters(self):
        for cl in self:
            for strain_id in cl.get_alphabetical_generator():
                yield strain_id, cl.id

    def gen_clusters(self, selected):
        """
        Generates Cluster objects according to the indices in the selected clusters list
        :param selected: the indices of the clusters to select
        :type selected: list
        :return: the generated cluster
        :rtype: Cluster
        """
        for i in selected:
            yield self[i]

    def compute_stats(self, id2strain, ngrams=1):
        for cl in self.clusters:
            cl.compute_distros(id2strain)
            cl.compute_tfs(id2strain, n_grams=ngrams)

    def print_clusters(self, selected_clusters='all', threshold=10, prec=2):
        if selected_clusters == 'all':
            selected_clusters = range(len(self))
        body, max_lens = self._get_rows(threshold=threshold, prob_precision=prec)
        header = self._get_header(max_lens, prec, selected_clusters)
        # header = ' - '.join('id:{} len:{}'.format(i, len(self[i])) + ' ' * (3-9 + prec + max_lens[i] - len(str(len(self[i])))) for i in selected_clusters) + '\n'
        print(header + body)

    def print_map(self):
        print(self.map_buffer)

    def _get_rows(self, threshold=10, prob_precision=3):
        max_token_lens = [max(map(lambda x: len(x[0]), cl.grams.most_common(threshold))) for cl in self.clusters]
        b = ''
        for i in range(threshold):
            b += ' | '.join('{} '.format(cl.grams.most_common(threshold)[i][0]) + ' '*(max_token_lens[j] - len(cl.grams.most_common(threshold)[i][0])) +
                            "{1:.{0}f}".format(prob_precision, cl.grams.most_common(threshold)[i][1] / len(cl)) for j, cl in enumerate(self.clusters)) + '\n'
        return b, max_token_lens


class Cluster:
    """
    An instance of this class encapsuates the behaviour of a single cluster estimated on some data. The object contains
    essential a "list" of the string ids ponting to unique datapoints.
    """
    def __init__(self, _id, members, active_variables):
        self.id = _id
        self.members = tuple(members)
        self.vars = active_variables
        self.freqs = OrderedDict()
        self.grams = None
        self._bytes = ''
        self._maxlen = 0

    def __str__(self):
        return 'cluster id: ' + str(self.id) + ',length: ' + str(len(self)) + '\n[' + ', '.join((_ for _ in self.get_alphabetical_generator())) + ']'

    def __len__(self):
        return len(self.members)

    def __iter__(self):
        return self

    def __next__(self):
        for strain_id in self.get_alphabetical_generator():
            yield strain_id

    def get_alphabetical_generator(self):
        return (_ for _ in sorted((s_id for s_id in self.members), reverse=False))

    def gen_ids(self):
        for _id in sorted((s_id for s_id in self.members), reverse=False):
            yield _id

    def compute_distros(self, id2strain):
        """
        This method calculates
        :param id2strain:
        :return:
        """
        counts = compute_counts(tuple(_ for _ in self.get_alphabetical_generator()), id2strain, self.vars)
        for var, value_counts in counts.items():
            if len(var) > self._maxlen:
                self._maxlen = len(var)
            norm = float(sum(value_counts.values()))
            self.freqs[var] = {k: v / norm for k, v in value_counts.items()}
        return self.freqs

    def compute_tfs(self, id2strain, field='_id', n_grams=1, normalizer='', word_filter='stopwords'):
        self.grams = Counter()
        for i, text in enumerate((extract_value(id2strain[iid], field) for iid in self.get_alphabetical_generator())):
            self.grams += Counter(gen_ngrams(text, n=n_grams, normalizer=normalizer, word_filter=word_filter))


def _make_counter_munchable(data, var):
    if var in enctype2features['binary-1'] or var in enctype2features['binary-on-off']:
        return [_ for _ in data]
    elif var in enctype2features['set-real-value']:
        return {k: v for k, v in data}


def compute_counts(iterable_of_ids, id2strain, variables):
    """
    This method calculates count statistics, based on the values of the variables carried by the input strain ids.\n
    :param iterable_of_ids: the collection of ids to compuite stats on (i.e. ('og-kush', 'silver') )
    :type iterable_of_ids: iterable
    :param id2strain:
    :type id2strain: dict
    :param variables:
    :type variables: iterable
    :return: the computed count statistics for the input strain id 'collection'
    :rtype: collections.OrderedDict
    """
    counts = OrderedDict(zip(variables, (Counter() for _ in variables)))
    for iid in iterable_of_ids:
        for var in variables:
            counts[var].update(_make_counter_munchable([_ for _ in gen_values(extract_value(id2strain[iid], var))], var))
    return counts


def gen_ngrams(text, n=1, normalizer='', word_filter='stopwords'):
    """
    This method creates and returns a generator of ngrams based on the input text, a normalizer and potentially a stopwords list.\n
    :param text: the raw unprocessed text
    :type text: str
    :param n: the degree of the grams desired to generate
    :type n: int
    :param normalizer:
    :type normalizer: str
    :param word_filter:
    :return:
    """
    if n == 1:
        return ('_'.join((_ for _ in gr)) for gr in nltk_ngrams(generate_tokens(text, normalizer=normalizer, word_filter=word_filter), n))
    else:
        return ('_'.join((_ for _ in gr)) for gr in nltk_ngrams(generate_tokens_with_padding(text, normalizer=normalizer, word_filter=word_filter), n))
