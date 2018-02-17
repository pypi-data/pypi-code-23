"""搜索算法
"""
from __future__ import print_function
from __future__ import division

# import operator
import math


# from decimal import Decimal


class BinSearch:

    @staticmethod
    def bin_search_float(lb, ub, target=3.14, cond_fn=lambda x, y: x <= y, precision=0.001, n_steps=100):
        """二分查找求解模板，一般用于求浮点值解
        本例的默认行为是求*大于*3.14 的最小值，精确到 3 位小数 (3.141)
        迭代固定次数可以回避终止条件，代价是多余的循环，
        比如本例取 (3,4) 为边界的话，只要6次就能找到满足条件的解，具体参考 `bin_search_float_while()`

        Notes:
            处理精度问题时，注意是 round, math.ceil 还是 math.floor
            这里应该是 math.ceil；因为返回值大概是 3.1400000001 这种形式
            此外，round 并不是精确的四舍五入，具体百度

        Args:
            lb (float or int): 解的搜索上限
            ub (float or int): 解的搜索下限
            target (float):
            cond_fn (callable): 条件函数
            precision (float): 精确到 precision 位小数
            n_steps (int): 迭代次数，默认值为 100
                100 次循环可以达到 10^(−30) 的精度，基本上能满足一般要求

        """
        for _ in range(n_steps):

            mid = lb + (ub - lb) / 2  # python 中的 / 默认是浮点除法

            if cond_fn(mid, target):  # 包含等号，已转为闭区间
                lb = mid
            else:
                ub = mid

        # 因为 lb 已经时闭区间，所以应该用 ub；当然这也应该视情况而定
        times = 1 / precision
        return math.ceil(ub * times) / times

    @staticmethod
    def bin_search_float_while(lb, ub, target=3.14, cond_fn=lambda x, y: x <= y, precision=0.001):
        """二分查找求解模板，不固定循环次数

        Args:
            lb:
            ub:
            target:
            cond_fn:
            precision:

        Returns:

        """

        while True:
            mid = lb + (ub - lb) / 2

            if cond_fn(mid, target):
                lb = mid
            else:
                ub = mid

            if 0 < mid - target < precision:
                break

        times = 1 / precision
        return math.ceil(ub * times) / times

    @staticmethod
    def bin_search(xs, target, cond_fn=lambda x, y: x < y):
        """二分查找通用模板，一般用来寻找正整数值
        通过指定条件函数 cond_fn 来搜索所需的值
        本例使用*闭区间*和`cond_fn`实现 lower_bound 相同的效果

        Notes:
            * 本例中将 (lb, ub) 看作闭区间
            * 不要苛求固定的模板

        Args:
            xs:
            target:
            cond_fn (callable): 条件函数，返回值应该是 bool 类型
                这里默认是*小于函数*

        """
        lb, ub = 0, len(xs) - 1

        while lb < ub:  # 闭区间，不使用 lb + 1 < ub
            mid = lb + (ub - lb) // 2

            if cond_fn(xs[mid], target):
                lb = mid + 1  # 一般不包含*等号*的地方需要 + 1，缩小区间
            else:
                ub = mid

        return lb  # 因为是闭区间，返回值也不需要 lb + 1

    @staticmethod
    def lower_bound(xs, target):
        """二分搜索 lower bound 版
        行为同 C++ <algorithm> 中的 lower_bound
        在给定升序数组中返回*大于等于* target 的最小索引；
        如果 target 大于数组中的最大值，返回 len(xs)

        Note:
            * 将 (lb, ub) 当作开区间，避免 lb = mid+1 或者 ub = mid-1 这种无谓的优化
                相应的，把 (lb, ub) 初始化为 (-1, n) 看作是 (-∞, +∞)
            * 有的问题可能当作闭区间更简单，不要苛求固定的模板

        Args:
            xs (list[int]): 有序数组
            target (int): 待查找的值

        Returns:
            int: 目标值（可能）的索引

        """
        lb, ub = -1, len(xs)  # (-1, n) 看作是 (-∞, +∞)

        while lb + 1 < ub:  # 既然是开区间，那么至少要有一个元素
            mid = lb + (ub - lb) // 2

            if xs[mid] < target:
                lb = mid
            else:
                ub = mid  # 因为包含等号，所以实际上这里的下界已经是*闭区间 (lb, ub]*了

        # 因为 lb 始终是开区间，所以需要返回 lb + 1，
        # 此时区间 (lb, ub] 内只有一个元素，所以返回 ub 也是一样的
        return lb + 1

    @staticmethod
    def upper_bound(xs, target):
        """二分搜索 upper bound 版
        行为同 C++ <algorithm> 中的 upper_bound
        在给定升序数组中返回*大于* target 的最小索引；
        注意只返回*大于* target 的索引，即使数组中包含 target
        如果 target 小于数组中的最小值，返回 0

        Args:
            xs (list[int]): 有序数组
            target (int): 待查找的值

        Returns:
            int: 目标值（可能）的索引

        """
        lb, ub = -1, len(xs)

        while lb + 1 < ub:
            mid = lb + (ub - lb) // 2

            if xs[mid] <= target:
                lb = mid  # 因为包含等号，这里实际上已经是*闭区间 [lb, ub)*了
            else:
                ub = mid

        # 最终区间内只有一个元素 [lb, ub)
        # 因为要满足 upper_bound 大于 target 的行为，这里依然返回的是 lb + 1
        return lb + 1


class DeepFirstSearch:

    @staticmethod
    def dfs_pseudo_code(current_state):
        """dfs 伪代码描述"""

        if "越界/不合法状态/达到递归深度":
            return

        if "达到终点/找到目标":
            return

        while "转移规则":
            if "下一个状态合法":
                # 相关操作
                # 标记当前状态
                # 是否剪枝
                DeepFirstSearch.dfs_pseudo_code(current_state + 1)  # 递归
                # 视情况是否还原标记
                # 还原标记相当于回溯，有的问题不需要回溯

    @staticmethod
    def dfs():
        pass
