
class Max(object):

	def __init__(self, keep_last=True):
            self.extreme_key = None
            self.extreme_item = None
            self.keep_last = keep_last
            self._is_draw = False

	def add(self, key, item):

            # The first item to ever be checked always wins
            if self.extreme_key is None:
                is_greater = True
                is_lesser = False

            # Later items get compared to the current winner.
            else:
                is_greater = self.comp(key, self.extreme_key)
                is_lesser = self.comp(self.extreme_key, key)

            # If we have a new winner, remember it.  It also means we don't
            # have a draw
            if is_greater:
                self._is_draw = False
                self.extreme_key = key
                self.extreme_item = item

            # If we don't have a winner, but it's also not a loser, then its a
            # tie.  Depending on the setting of ``keep_last``, we might keep
            # the newer item instead of the prior one.
            elif not is_lesser:
                self._is_draw = True
                if self.keep_last:
                    self.extreme_key = key
                    self.extreme_item = item


        def is_draw(self):
            return self._is_draw


	def update(self, key_item_pairs):
		for key, item in key_item_pairs:
			self.add(key, item)

	def get(self):
		return self.extreme_key, self.extreme_item

	def comp(self, key1, key2):
		return key1 > key2


class Min(Max):
	def comp(self, key1, key2):
		return key1 < key2
