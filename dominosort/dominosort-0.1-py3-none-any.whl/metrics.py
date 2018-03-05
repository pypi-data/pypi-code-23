from .norms import Norm, L1Norm, L2Norm
from .utils import alias


class Metric:
    norm = Norm

    @classmethod
    def eval(cls, x1, x2):
        return cls.norm(x1 - x2)


@alias('L1Distance')
@alias('ManhattanMetric')
class ManhattanDistance(Metric):
    norm = L1Norm


@alias('L2Distance')
@alias('EuclideanMetric')
class EuclideanDistance(Metric):
    norm = L2Norm
