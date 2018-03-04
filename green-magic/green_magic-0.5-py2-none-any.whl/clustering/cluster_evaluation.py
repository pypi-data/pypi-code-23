import numpy as np
from sklearn.metrics import silhouette_score, calinski_harabaz_score


class ModelQualityReporter(object):
    """
    - Reference: http://scikit-learn.org/stable/modules/clustering.html#clustering-evaluation

    This class is able to calculate scores based on different model evaluation metrics.
    Supported metrics are:

    * 'silhouette' for the Silhouette Coefficient in [-1, 1]: where a higher Silhouette Coefficient score relates to a model with better defined clusters.
        -- The score is bounded between -1 for incorrect clustering and +1 for highly dense clustering. Scores around zero indicate overlapping clusters.\n
        -- The score is higher when clusters are dense and well separated, which relates to a standard concept of a cluster.
    * 'cali-hara' for the Calinski-Harabaz index in []: where a higher Calinski-Harabaz score relates to a model with better defined clusters.
        -- The score is higher when clusters are dense and well separated, which relates to a standard concept of a cluster.\n
        -- The score is fast to compute
    """

    def __init__(self, strain_id2datapoint):
        self.strain_id2datapoint = strain_id2datapoint
        self.methods = {
            # 'silhouette': metrics.silhouette_score(X, labels, metric='euclidean')
            'silhouette': silhouette_score,
            'cali-hara': calinski_harabaz_score
        }
        self.clustering = None
        self.metric = ''
        self.score = None

    def __str__(self):
        return '\'{}\' on \'{}\' clustering nb_clusters={} : {:.2f}'.format(self.metric, self.clustering.id, len(self.clustering), self.score)

    def measure(self, clustering, metric='silhouette'):
        """
        Calculates and returns an evaluation score based on the given metric on a Clustering.\n
        :param clustering: the Clustering object to evaluate
        :type clustering: clustering.Clustering
        :param metric: defines the evaluation formula/method
        :type metric: str
        :return: the calculated score
        :rtype: float
        """
        array = np.array([res for res in clustering.gen_ids_and_assigned_clusters()])
        arr1 = np.array([self.strain_id2datapoint[iid] for iid in array[:, 0]])
        self.clustering = clustering
        self.metric = metric
        self.score = self.methods[metric](arr1, array[:, 1])
        return self

    def evaluate(self, clustering, metric='', **kwargs):
        """
        Evaluates using a metric that utilizes the ground truth (class labels) to compute the score.\n
        :param clustering:
        :param metric:
        :param kwargs:
        :return:
        """
        # TODO implement body
        pass


def get_model_quality_reporter(weedmaster, weedataset_id):
    return ModelQualityReporter(weedmaster[weedataset_id].dt.id2datapoint)
