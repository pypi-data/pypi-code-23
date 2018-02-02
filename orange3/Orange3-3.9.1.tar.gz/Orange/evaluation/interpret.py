import numpy as np
from lime.lime_tabular import LimeTabularExplainer

from Orange.data import Table, Instance
from Orange.classification import RandomForestLearner


__all__ = ['LimeTabular']

np.random.seed(1)


class LimeTabular:
    """Wrapper for lime"""
    def __init__(self, train, model, seed=None, **kwargs):
        self.train = train
        self.model = model
        self.seed = seed
        self.proba = lambda x: model(x, 1)

        train = Table(model.domain, train)
        feature_names = [f.name for f in train.domain.attributes]
        class_names = train.domain.class_var.values
        self.explainer = LimeTabularExplainer(train.X, feature_names=feature_names, class_names=class_names, **kwargs)

    def _explain_instance(self, instance, label=None, save_html='/tmp/explanation.html'):
        if self.seed is not None:
            np.random.seed(self.seed)
        exp = self.explainer.explain_instance(instance, self.proba, top_labels=1)
        exp.save_to_file(save_html)
        return exp.as_map()

    def __call__(self, data):
        if isinstance(data, Instance): # or isinstance(data, np.array) and len(data.shape) == 1:
            data = Instance(self.model.domain, data)
            return self._explain_instance(data._x)
        #res = []
        #for ins in data:
        #    res.append(self.explain_instance(ins))
        return self._explain_instance(Table(self.model.domain, data)[0]._x)


def test():
    data = Table('titanic')
    train = data[::2]
    test = data[1::2]
    rf = RandomForestLearner()
    model = rf(train)
    print(model(test, 1))
    lime = LimeTabular(train, model, discretize_continuous=False)
    print(lime(test[11]))


class LimeOrange:
    def __init__(self, train, model, seed=None):
        self.train = train
        self.model = model
        self.seed = seed

        train = Table(model.domain, train)

    def explain_instance(self, data_row, classifier_fn, labels=(1,),
                         top_labels=None, num_features=10, num_samples=5000,
                         distance_metric='euclidean', model_regressor=None):
        """Generates explanations for a prediction.

        First, we generate neighborhood data by randomly perturbing features
        from the instance (see __data_inverse). We then learn locally weighted
        linear models on this neighborhood data to explain each of the classes
        in an interpretable way (see lime_base.py).

        Args:
            data_row: 1d numpy array, corresponding to a row
            classifier_fn: classifier prediction probability function, which
                takes a numpy array and outputs prediction probabilities.  For
                ScikitClassifiers , this is classifier.predict_proba.
            labels: iterable with labels to be explained.
            top_labels: if not None, ignore labels and produce explanations for
                the K labels with highest prediction probabilities, where K is
                this parameter.
            num_features: maximum number of features present in explanation
            num_samples: size of the neighborhood to learn the linear model
            distance_metric: the distance metric to use for weights.
            model_regressor: sklearn regressor to use in explanation. Defaults
            to Ridge regression in LimeBase. Must have model_regressor.coef_
            and 'sample_weight' as a parameter to model_regressor.fit()

        Returns:
            An Explanation object (see explanation.py) with the corresponding
            explanations.
        """
        data_row = Instance(self.model.domain, data_row)
        data, inverse = self.__data_inverse(data_row, num_samples)
        scaled_data = (data - self.scaler.mean_) / self.scaler.scale_

        distances = sklearn.metrics.pairwise_distances(
            scaled_data,
            scaled_data[0].reshape(1, -1),
            metric=distance_metric
        ).ravel()

        yss = classifier_fn(inverse)
        if self.class_names is None:
            self.class_names = [str(x) for x in range(yss[0].shape[0])]
        else:
            self.class_names = list(self.model.domain.class_var.values)
        feature_names = copy.deepcopy(self.feature_names)
        if feature_names is None:
            feature_names = [str(x) for x in range(data_row.shape[0])]

        def round_stuff(x):
            return ['%.2f' % a for a in x]

        values = round_stuff(data_row)
        for i in self.categorical_features:
            if self.discretizer is not None and i in self.discretizer.lambdas:
                continue
            name = int(data_row[i])
            if i in self.categorical_names:
                name = self.categorical_names[i][name]
            feature_names[i] = '%s=%s' % (feature_names[i], name)
            values[i] = 'True'
        categorical_features = self.categorical_features
        discretized_feature_names = None
        if self.discretizer is not None:
            categorical_features = range(data.shape[1])
            discretized_instance = self.discretizer.discretize(data_row)
            discretized_feature_names = copy.deepcopy(feature_names)
            for f in self.discretizer.names:
                discretized_feature_names[f] = self.discretizer.names[f][int(
                    discretized_instance[f])]

        domain_mapper = TableDomainMapper(
            feature_names, values, scaled_data[0],
            categorical_features=categorical_features,
            discretized_feature_names=discretized_feature_names)
        ret_exp = explanation.Explanation(domain_mapper=domain_mapper,
                                          class_names=self.class_names)
        ret_exp.predict_proba = yss[0]
        if top_labels:
            labels = np.argsort(yss[0])[-top_labels:]
            ret_exp.top_labels = list(labels)
            ret_exp.top_labels.reverse()
        for label in labels:
            (ret_exp.intercept[label],
             ret_exp.local_exp[label],
             ret_exp.score) = self.base.explain_instance_with_data(
                scaled_data, yss, distances, label, num_features,
                model_regressor=model_regressor,
                feature_selection=self.feature_selection)
        return ret_exp

    def __data_inverse(self, data_row, num_samples):
        """Generates a neighborhood around a prediction.

        For numerical features, perturb them by sampling from a Normal(0,1) and
        doing the inverse operation of mean-centering and scaling, according to
        the means and stds in the training data. For categorical features,
        perturb by sampling according to the training distribution, and making
        a binary feature that is 1 when the value is the same as the instance
        being explained.

        Args:
            data_row: 1d numpy array, corresponding to a row
            num_samples: size of the neighborhood to learn the linear model

        Returns:
            A tuple (data, inverse), where:
                data: dense num_samples * K matrix, where categorical features
                are encoded with either 0 (not equal to the corresponding value
                in data_row) or 1. The first row is the original instance.
                inverse: same as data, except the categorical features are not
                binary, but categorical (as the original data)
        """
        data = np.zeros((num_samples, data_row.shape[0]))
        categorical_features = range(data_row.shape[0])
        if self.discretizer is None:
            data = np.random.normal(
                0, 1, num_samples * data_row.shape[0]).reshape(
                num_samples, data_row.shape[0])
            data = data * self.scaler.scale_ + self.scaler.mean_
            categorical_features = self.categorical_features
            first_row = data_row
        else:
            first_row = self.discretizer.discretize(data_row)
        data[0] = data_row.copy()
        inverse = data.copy()
        for column in categorical_features:
            values = self.feature_values[column]
            freqs = self.feature_frequencies[column]
            inverse_column = np.random.choice(values, size=num_samples,
                                              replace=True, p=freqs)
            binary_column = np.array([1 if x == first_row[column]
                                      else 0 for x in inverse_column])
            binary_column[0] = 1
            inverse_column[0] = data[0, column]
            data[:, column] = binary_column
            inverse[:, column] = inverse_column
        if self.discretizer is not None:
            inverse[1:] = self.discretizer.undiscretize(inverse[1:])
        inverse[0] = data_row
        return data, inverse

if __name__ == '__main__':
    #test()
    pass


"""
train, test, labels_train, labels_test = sklearn.model_selection.train_test_split(iris.data, iris.target, train_size=0.80)

rf = sklearn.ensemble.RandomForestClassifier(n_estimators=500)
rf.fit(train, labels_train)

sklearn.metrics.accuracy_score(labels_test, rf.predict(test))

explainer = lime.lime_tabular.LimeTabularExplainer(train, feature_names=iris.feature_names, class_names=iris.target_names, discretize_continuous=True)

i = np.random.randint(0, test.shape[0])
exp = explainer.explain_instance(test[i], rf.predict_proba, num_features=2, top_labels=1)

#exp.show_in_notebook(show_table=True, show_all=False)
#exp.as_list()
exp.save_to_file('/tmp/oi.html')


"""
