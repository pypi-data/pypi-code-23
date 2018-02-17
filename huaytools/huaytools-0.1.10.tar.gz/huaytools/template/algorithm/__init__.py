"""算法模板
该模块不是为了构建通用算法API，而是用最简单的代码记录算法的实现过程，
不包括任何*算法外*的异常处理

Attributes:
    bin_search_float: 二分查找求解模板，一般用于求浮点值解
"""

from . import search
from .search import BinSearch
from .search import DeepFirstSearch

bin_search_float = BinSearch.bin_search_float
"""二分查找求解模板，一般用于求浮点值解"""

bin_search = BinSearch.bin_search
"""二分查找通用模板，一般用来寻找正整数值"""

lower_bound = BinSearch.lower_bound
"""二分搜索 lower bound 版"""

upper_bound = BinSearch.upper_bound
"""二分搜索 upper bound 版"""

dfs_pseudo_code = DeepFirstSearch.dfs_pseudo_code
"""dfs 伪代码描述"""
