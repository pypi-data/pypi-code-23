"""Iteration utilities"""

class Batch:
    """Yields batches (groups) from an iterable

    Modified from:
    http://codereview.stackexchange.com/questions/118883/split-up-an-iterable-into-batches

    Args:
        iterable (iterable) any iterable
        limit (int) How many items to include per group
    """
    def __init__(self, iterable, limit=None):
        self.iterator = iter(iterable)
        self.limit = limit
        try:
            self.current = next(self.iterator)
        except StopIteration:
            self.on_going = False
        else:
            self.on_going = True

    def group(self):
        """Yield a group from the iterable"""
        yield self.current
        # start enumerate at 1 because we already yielded the last saved item
        for num, item in enumerate(self.iterator, 1):
            self.current = item
            if num == self.limit:
                break
            yield item
        else:
            self.on_going = False

    def __iter__(self):
        """Implementation of __iter__ to allow a standard interface:

        for group in Batch(iterable, 10):
            do_stuff(group)
        """

        while self.on_going:
            yield self.group()
