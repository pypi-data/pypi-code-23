# -*- coding: utf-8 -*-

from __future__ import division

import random
from decimal import Decimal

from .compat import range


ZERO_VALUE = 'Zero Value of Param {}'
INVALID_VALUE = 'Invalid Value for Num: \'{}\''
TRIPLE_INVALID_VALUE = 'Invalid Value for Total-{}, Num-{}, Min-{}'


class RedPackets(object):
    def decimal(self, value):
        """
        In [1]: Decimal(3.14)
        Out[1]: Decimal('3.140000000000000124344978758017532527446746826171875')

        In [2]: Decimal(str(3.14))
        Out[2]: Decimal('3.14')
        """
        return Decimal(str(value))

    def split_dollar_val(self, min, max):
        return min if min > max else self.decimal(random.randint(min, max))

    def split_dollar(self, total, num, min=0.01):
        """
        RedPackets Split for Dollar

        :param total: Total Value of RedPackets
        :param num: Split Num of RedPackets
        :param min: Limit Value of Each Split
        """
        if not (total and num):
            raise ValueError(ZERO_VALUE.format('Num' if total else 'Total'))

        # Convert and Check of Total
        total = self.decimal(total)

        # Convert and Check of Num
        if isinstance(num, float) and int(num) != num:
            raise ValueError(INVALID_VALUE.format(num))
        num = self.decimal(int(num))

        # Convert and Check of Min
        min = self.decimal(min)

        # Compare Total and Num * Min
        if total < num * min:
            raise ValueError(TRIPLE_INVALID_VALUE.format(total, num, min))

        split_list = []
        for i in range(1, int(num)):
            # Random Safety High Limit Total
            safe_total = (total - (num - i) * min) / (num - i)
            split_val = self.split_dollar_val(min * 100, int(safe_total * 100)) / 100
            total -= split_val
            split_list.append(split_val)
        split_list.append(total)

        # Random Disarrange
        random.shuffle(split_list)

        return split_list

    def split_cent_val(self, min, max):
        return min if min > max else random.randint(min, max)

    def split_cent(self, total, num, min=1):
        """
        RedPackets Split for Cent

        :param total: Total Value of RedPackets
        :param num: Split Num of RedPackets
        :param min: Limit Value of Each Split
        """
        if not (total and num):
            raise ValueError(ZERO_VALUE.format('Num' if total else 'Total'))

        # Convert and Check of Total, Num, Min
        total, num, min = int(total), int(num), int(min)

        # Compare Total and Num * Min
        if total < num * min:
            raise ValueError(TRIPLE_INVALID_VALUE.format(total, num, min))

        split_list = []
        for i in range(1, int(num)):
            # Random Safety High Limit Total
            safe_total = (total - (num - i) * min) / (num - i)
            split_val = int(self.split_cent_val(min * 100, int(safe_total * 100)) / 100)
            total -= split_val
            split_list.append(split_val)
        split_list.append(total)

        # Random Disarrange
        random.shuffle(split_list)

        return split_list

    def split(self, total, num, min=None, cent=False):
        """
        RedPackets Split for Dollar or Cent

        :param total: Total Value of RedPackets
        :param num: Split Num of RedPackets
        :param min: Limit Value of Each Split
        :param cent: Split for Dollar or Cent
        """
        return self.split_cent(total, num, min or 1) if cent else self.split_dollar(total, num, min or 0.01)

    def cent(self, dollar, rate=100, cast_func=int):
        """
        Exchange Dollar into Cent

        In [1]: 0.07 * 100
        Out[1]: 7.000000000000001

        :param dollar:
        :param rate:
        :return:
        """
        return self.mul(dollar, rate, cast_func=cast_func)

    def dollar(self, cent, rate=100, cast_func=float):
        """
        Exchange Cent into Dollar

        :param cent:
        :param rate:
        :return:
        """
        return self.div(cent, rate, cast_func=cast_func)

    def mul(self, multiplicand, multiplicator, cast_func=float):
        """
        8 × 3 = 24, 8 is multiplicand, 3 is multiplicator.
        """
        return cast_func(self.decimal(multiplicand) * self.decimal(multiplicator))

    def div(self, dividend, divisor, cast_func=float):
        """
        24 ÷ 8 = 3, 24 is dividend, 8 is divisor.
        """
        return cast_func(self.decimal(dividend) / self.decimal(divisor))


_global_instance = RedPackets()
split_dollar = split_Yuan = _global_instance.split_dollar
split_cent = split_Fen = _global_instance.split_cent
split = _global_instance.split
cent = Fen = dollar2cent = Yuan2Fen = _global_instance.cent
dollar = Yuan = cent2dollar = Fen2Yuan = _global_instance.dollar
mul = _global_instance.mul
div = _global_instance.div
# Spelling mistake. For backwards compatibility
split_dollor = _global_instance.split_dollar
dollor = _global_instance.dollar
