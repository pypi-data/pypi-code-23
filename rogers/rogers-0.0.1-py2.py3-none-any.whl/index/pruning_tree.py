""" Uses https://github.com/facebookresearch/pysparnn which is based on idea of
cluster pruning trees, https://nlp.stanford.edu/IR-book/html/htmledition/cluster-pruning-1.html
"""
import pysparnn.cluster_index as ci

from . import Index as BaseIndex


class Index(BaseIndex):
    """ Pruning Tree Index
    """

    name = 'pruning_tree'

    def fit(self, samples, **kwargs):
        """ Fit index
        :param samples: list of Samples
        :param kwargs:
        :return:
        """
        xs, self.ys = self.transform(samples)
        self.index = ci.MultiClusterIndex(xs, self.ys)

    def _query(self, sample,  k=5, **kwargs):
        """ Query index
        :param sample:
        :param k:
        :param kwargs: k_clusters: number of branches (leader clusters) to search at each level h

        :return:
        """
        k_clusters = kwargs.get('k_clusters', 50)
        x, _, = self.transform([sample])
        results = self.index.search(x, k=k+1, k_clusters=k_clusters)
        return [{'hashval': n[1], 'similarity': 1 - float(n[0])} for n in results[0]]