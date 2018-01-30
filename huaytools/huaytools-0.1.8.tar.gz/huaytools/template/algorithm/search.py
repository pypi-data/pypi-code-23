"""搜索算法
"""
from __future__ import print_function
from __future__ import division

# import operator
import math
# from decimal import Decimal


class BinSearch:

    @staticmethod
    def bin_search_float(lb, ub, cond_fn=lambda x: x <= 3.14, precision=3, n_steps=100):
        """二分查找求解模板，一般用于求浮点值解
        本例的默认行为是求*大于*3.14 的最小值，精确到 3 位小数 (3.141)

        Notes:
            处理精度问题时，注意是 round, math.ceil 还是 math.floor
            这里应该是 math.ceil；因为返回值大概是 3.1400000001 这种形式
            此外，round 并不是精确的四舍五入，具体百度

        Args:
            lb (float or int): 解的搜索上限
            ub (float or int): 解的搜索下限
            cond_fn (callable): 条件函数
            precision (int): 精确到 precision 位小数
            n_steps (int): 迭代次数，默认值为 100
                100 次循环可以达到 10^(−30) 的精度，基本上能满足一般要求

        """
        for _ in range(n_steps):

            mid = lb + (ub - lb) / 2  # python 中的 / 默认是浮点除法

            if cond_fn(mid):
                lb = mid
            else:
                ub = mid

        return math.ceil(ub * 10**precision) / 10**precision

    @staticmethod
    def bin_search(xs, cond_fn=lambda x: x < 5):
        """二分查找通用模板，一般用来寻找正整数值
        通过指定条件函数 cond_fn 来搜索指定要求的值
        本例的默认行为是找出*大于等于5* 的最大值（的索引）

        Notes:
            * 本例的目标是为了找出*大于等于5* 的最大值（的索引）
                使用的 cond_fn 却是 < , 这与函数内部的 if-else,
                以及返回值的选择都有关系，这也是`二分查找`最烦人的地方
            * 本例中将 (lb, ub) 看作开区间，避免 lb = mid+1 或者 ub = mid-1 的讨论
                但是有的问题当作闭区间会更简单
            * 不要苛求固定的模板

        Args:
            xs:
            cond_fn (callable): 条件函数，返回值应该是 bool 类型
                该函数应该只接收一个参数 xs[mid]，如果需要多个参数
                可以通过 lambda 来封装其他参数，如本例所示

        """
        lb, ub = -1, len(xs)

        while lb + 1 < ub:
            mid = lb + (ub - lb) // 2

            if cond_fn(xs[mid]):
                lb = mid
            else:
                ub = mid

        return lb + 1

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
                ub = mid

        return lb + 1  # 同样因为开区间，所以需要返回 lb+1

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
                lb = mid
            else:
                ub = mid

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