
class Standardize():
    @staticmethod
    def torch(x):
        import torch
        import numpy as np
        """
            Preprocessing the x data with zero meand and unitary variance
            Arguments:
                        x -- numpy ndarray
            Returns:
                        standardized -- data standardize (torch Tensor)
        """

        # Convert to Tensor
        if isinstance(x, np.ndarray):
            x = torch.from_numpy(x)

        standardized = (torch.div(x - torch.mean(x, 0), torch.std(x, 0)))
        return standardized

    @staticmethod
    def numpy(x, bessel_correction=True):
        import numpy as np
        """
            Preprocessing the x data with zero meand and unitary variance
            Arguments:
                        x -- numpy ndarray
            Returns:
                        standardized -- data standardize (numpy ndarray)
        """
        if bessel_correction:
            standardized = (x - np.mean(x, 0)) / np.std(x, 0, ddof=1)
        else:
            standardized = (x - np.mean(x, 0)) / np.std(x, 0)

        return standardized


class Normalize():
    def torch(x):
        import torch
        import numpy as np
        """
                Preprocessing the x data with zero meand and unitary variance
                Arguments:
                            x -- numpy ndarray
                Returns:
                            standardize -- data standardize (torch Tensor)
            """
        # Convert to Tensor
        if isinstance(x, np.ndarray):
            x = torch.from_numpy(x)

        max_ = torch.max(x, 0)[0]
        normilized = torch.div(x, max_)

        return normilized

    @staticmethod
    def numpy(x):
        import numpy as np
        """
                Preprocessing the x data with zero meand and unitary variance
                Arguments:
                            x -- numpy ndarray
                Returns:
                            standardize -- data standardize (numpy ndarray)
            """

        normilized = x / x.max(axis=0)

        return normilized
