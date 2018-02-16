
from .roll_scale import ROLLS

MAX_INDEX = len(ROLLS) - 1

MAX_PRICE = 501


def price_rounder(price, rolls=0):
    """ Rounds price to nearest dividend found in roll_scale.ROLLS.
    If rolls is non-zero, returns the zero roll equivalent of the price.

    :param price: price to be matched to dividend
    :param roll: number of rolls applied to price by trader.

    E.g.:
    If price is 1.82 and roll is +2, then returns 1.80 as applying
    2 positive rolls to 1.80 gives 1.82.
    """

    # 8/10/2017: Modified to use SortedList and binary search capability.
    #            Achieved ~7x speedup over previous implementation where
    #            rounding non-exact prices.

    # No logging in this function as it will generally be called in tight
    # loops.

    try:
        index = ROLLS.index(price)
    except ValueError:
        r_ind = ROLLS.bisect_left(price)
        l_ind = r_ind - 1

        if l_ind < 0:
            l_ind = 0

        if r_ind > MAX_INDEX:
            r_ind = MAX_INDEX

        l_diff = abs(price - ROLLS[l_ind])
        r_diff = abs(price - ROLLS[r_ind])

        if l_diff < r_diff:
            index = l_ind
        else:
            index = r_ind

    try:
        price = ROLLS[index - rolls]
        return price if price < MAX_PRICE else MAX_PRICE
    except IndexError:
        return 0
