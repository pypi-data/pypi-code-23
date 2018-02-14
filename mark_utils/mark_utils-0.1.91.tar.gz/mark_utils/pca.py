

class PCA():

    @staticmethod
    def torch(x, k):
        """
            Reduce dimensionality with the principal components analisys.
            Using torch library. (more accurate then numpy)
            Arguments:
                x -- numpy ndarray or torch tensor
                k -- dimensionality of the output
            Returns:
                components -- data projected into a lower dimensionality
        """
        import torch
        import numpy as np

        # Convert to DoubleTensor
        if isinstance(x, np.ndarray):
            x = torch.from_numpy(x)

        # SVD
        U, S, V = torch.svd(x.t())
        components = torch.mm(x, U[:, :k])

        return - components

    @staticmethod
    def numpy(x, k):
        """
                Reduce dimensionality with the principal components analisys.
                Using sklearn.decomposition
                Arguments:
                    x -- numpy ndarray or torch tensor
                    k -- dimensionality of the output
                Returns:
                    components -- data projected into a lower dimensionality
        """
        from sklearn.decomposition import PCA

        pca = PCA(k)
        components = pca.fit_transform(x)

        return components


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from sklearn import datasets
    from mark_utils.preprocessing import Standardize
    import numpy as np

    iris = datasets.load_iris()
    x = iris.data
    y = iris.target

    x = Standardize.torch(x)
    x_pca = PCA.torch(x, 2)

    # To numpy
    x_pca = x_pca.numpy()

    plt.figure()

    for i, target_name in enumerate(iris.target_names):
        plt.scatter(x_pca[y == i, 0], x_pca[y == i, 1], label=target_name)

    plt.legend()
    plt.title('PCA of IRIS dataset')
    plt.show()
