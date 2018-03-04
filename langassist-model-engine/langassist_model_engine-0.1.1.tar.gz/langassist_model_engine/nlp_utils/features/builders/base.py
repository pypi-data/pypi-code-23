class BaseFeaturizer():
    '''
        This is the base class for a feature builder. A feature builder should take text
        data as input and return the numerical features which represent the text
        Implement the `featurize_all()` method if you intend to pass a series of samples
        Implement the `featurize()` method to convert a single string into a feature vector
    '''
    def __init__(self):
        pass

    def featurize_all(self, samples):
        '''
        The intended way this method should work:
            Samples is expected as a Pandas DataFrame
            The return type should be a Scipy csr sparse matrix
        :param samples:
        :return:
        '''
        raise NotImplementedError

    def featutize(self, text):
        '''
            This method should turn a single string into a Scipy csr sparse matrix
            This method will be used by `featurize_all()`
        :param text:
        :return:
        '''
        raise NotImplementedError