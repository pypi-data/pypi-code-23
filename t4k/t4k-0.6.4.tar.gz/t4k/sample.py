import random

class ReservoirSampler(object):

    def __init__(self, k):
        self.sample = []
        self.k = k
        self.i = 0


    def add(self, item):
        """
        Possibly add an item to the sample.  The probability that an item will
        be kept is continually decreased as more items are considered such, at
        any given time, all items that have been considered so far have an
        equal chance of being part of the set.
        """

        # Increment the counter for the number of items considered
        i = self.i
        self.i += 1

        # If we don't yet have k samples, then we definitely include the item
        if i < self.k:
            self.sample.append(item)
            return True

        # Otherwise, we *might* keep the item (replacing a previously kept
        # item).  The probability adjusts as we go along so that all items are
        # given uniform chance of being in the final set if retained items
        else:
            pick = random.randint(0, i)
            if pick < self.k:
                self.sample[pick] = item
                return True

        return False


    def add_many(self, iterable, allow_small_sample=False):
        """
        Consider each element yielded by the iterable for inclusion in the
        sample.  If allow_small_sample is False, then, if fewer than self.k
        items are in the sample after the iterable is exhausted, an exception
        will be raised.
        """
        for item in iterable:
            self.add(item)

        if len(self.sample) < self.k and not allow_small_sample:
            raise ValueError('Population smaller than sample size')


def reservoir_sample(iterable, k, allow_small_sample=False):
    """
    Convenience function to retrieve a reservior sample from an iterable
    """
    sampler = ReservoirSampler(k)
    sampler.add_many(iterable, allow_small_sample)
    return sampler.sample


