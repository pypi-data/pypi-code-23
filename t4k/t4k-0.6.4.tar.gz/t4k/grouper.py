import itertools
import numpy as np
import random
import math
import hashlib


def skip_blank(iterable):
    return itertools.ifilter(lambda x: x.strip()!='', iterable)


def trimmed_nonblank(iterable):
    for line in skip_blank(iterable):
        yield line.strip()


def skipfirst(iterable):
    iterator = iter(iterable)
    iterator.next()
    return iterator


def get_fold(data, num_folds, this_fold):
    """
    Randomly, but reproducibly separate out 1/num_folds of ``data`` as a
    validation set.

    By varying ``this_fold`` from 0 to ``num_folds - 1``, obtain different
    splits of the data such that the validations sets do not overlap and all
    data appear in some validation set.
    """
    if this_fold < 0 or this_fold >= num_folds:
        raise ValueError('``this_fold`` must be in [0,num_folds-1]')

    # Reproducibly create a random permutation
    random.seed(0)
    permutation = range(len(data))
    random.shuffle(permutation)

    # Get the slice of the random permutation that will correspond to the test
    # part of the fold
    start = int(this_fold * float(len(data)) / num_folds)
    end = int((this_fold+1) * float(len(data)) / num_folds)
    fold_test_indices = permutation[start:end]

    # Everything else is the training part of the fold
    fold_train_indices = permutation[:start] + permutation[end:]

    fold_test = np.array([data[i] for i in fold_test_indices])
    fold_train = np.array([data[i] for i in fold_train_indices])
    return fold_train, fold_test




class IncrementingMap(dict):

    def add(self, key):
        if key not in self:
            self[key] = self.get_incrementing_id()
            self._get_keys().append(key)


    def add_many(self, keys_iterator):
        for key in keys_iterator:
            self.add(key)


    def get_incrementing_id(self):
        try:
            self._current_id += 1
        except AttributeError:
            self._current_id = 0
        return self._current_id


    def _get_keys(self):
        '''
        This getter is private, and covers the case where self._keys is not 
        yet defined.  The first time it is called, self._keys is initialized
        to be an empty list.
        '''
        try:
            return self._keys
        except AttributeError:
            self._keys = []
            return self._keys


    def key(self, idx):
        return self._get_keys()[idx]


    def keys(self):
        return [k for k in self._get_keys()]



def _validate_normalize_slice_indices(list_obj, start, stop):

    # Fail if list_item doesn't support indexing
    if not hasattr(list_obj, '__getitem__'):
        raise ValueError('Cannot index into list_obj.')

    # Fail if list_item doesn't support indexing
    if not hasattr(list_obj, '__getitem__'):
        raise ValueError('Cannot index into list_obj.')

    # If stop is not defined, set it equal to len(list_obj)
    the_len = len(list_obj)
    if stop is None:
        stop = the_len

    # Convert negative indices into equivalent positive form
    if start < 0:
        start = start + the_len
    if stop < 0:
        stop = stop + the_len

    # trim start and stop to within the list's actual length
    start = max(0, start)
    stop = min(the_len, stop)

    ## Fail if start is greater than stop
    #if start > stop:
    #       raise ValueError('start cannot be greater than stop.')

    return start, stop


def ltrim(list_obj, item=0):
    match = lambda x: x!=item
    start = lindex(list_obj,match_func=match) 
    return list_obj[start:]

def rtrim(list_obj, item=0):
    match = lambda x: x!=item
    stop = rindex(list_obj,match_func=match)+1
    return list_obj[:stop]

def trim(list_obj, item=0):
    match = lambda x: x!=item
    start = lindex(list_obj,match_func=match) 
    stop = rindex(list_obj,match_func=match)+1
    return list_obj[start:stop]


def lindex(list_obj, item=None, match_func=None, start=0, stop=None):

    ''' 
    find the index of first occurence of <item> in <list_obj>, within 
    the slice defined by <start> and <stop>.  Start and stop work
    the way normal list slicing does.  By default, start is 0 and stop
    is the length of the list.  If stop is not given, <list_obj> must
    define __len__().
    '''

    start, stop = _validate_normalize_slice_indices(list_obj, start, stop)

    if match_func == None:
        if item is None:
            raise ValueError(
                'Either `item` or `match_func` must be specified')
        match_func = lambda x: x==item

    # find the index of item
    cur_idx = start
    while cur_idx < stop:
        try:
            if match_func(list_obj[cur_idx]):
                return cur_idx
        except IndexError:
            pass
        cur_idx += 1

    # Item is not in the list
    raise ValueError('No match in list.')



def rindex(list_obj, item=None, match_func=None, start=0, stop=None):

    ''' 
    find the index of first occurence of <item> in <list_obj>, within 
    the slice defined by <start> and <stop>.  Start and stop work
    the way normal list slicing does.  By default, start is 0 and stop
    is the length of the list.  If stop is not given, <list_obj> must
    define __len__().
    '''

    start, stop = _validate_normalize_slice_indices(list_obj, start, stop)

    if match_func == None:
        if item is None:
            raise ValueError(
                'Either `item` or `match_func` must be specified')
        match_func = lambda x: x==item

    # find the index of item
    cur_idx = stop - 1
    while cur_idx >= start:
        try:
            if match_func(list_obj[cur_idx]):
                return cur_idx
        except IndexError:
            pass
        cur_idx -= 1

    # Item is not in the list
    raise ValueError('No match in list')


def indices(list_obj, item, start=0, stop=None):
    idxs = []

    try:
        while True:
            idx = lindex(list_obj, item, start, stop)
            idxs.append(idx)
            start = idx + 1
    except ValueError:
        pass

    return idxs
        

def skip(list_obj, skip_slices):
    '''
    Returns a copy of list obj with elements ommited.  The ommited elements
    are specified by skip_slices, a list of tuples specifying spans of
    elements to skip using slice notation.

    -- Input --
    skip_slices: a list of 2-tuples, each consisting of start and stop
        indices specifying spans of elements to be ommitted from list_obj
        
    list_obj: a list.
    
    -- Returns --
    censored_list: a list that doesn't contain the elements that
        would be selected by treating the tuples in skip_slices as
        slice indices.
    '''

    # We begin by normalizing the slice indices.  First, convert all
    # occurrences of None into integers.  
    skip_slices_no_none = []
    for start, stop in skip_slices:

        # When None is used as a start index, it is equivalent to 0
        if start is None:
            start = 0

        # When None is used as a stop index, it is equivalent to len(list)
        if stop is None:
            stop = len(list_obj)

        # Append the equivalent slice defined using only integers
        skip_slices_no_none.append((start,stop))
    
    # To assemble the 
    # censored list, we need the slice indices sorted by start-index.
    # We also need to handle cases where the spans defined by slice
    # indices overlap.  When slice indices overlap, there are two cases.
    # In the simple case, the spans overlap a little, but in the second
    # case, the first span subsumes the second.  We need to eliminate
    # occurrences of the second kind.  We can simply drop the subsumed
    # span since it is redundant anyway.
    normalized_skip_slices = []
    for i, (start, stop) in enumerate(sorted(skip_slices_no_none)):

        # On the first iteration, just keep the first slice and move on
        if i == 0:
            normalized_skip_slices.append((start,stop))
            prev_start, prev_stop = start, stop

        # This means that the current slice is subsumed by the previous.
        # We simply don't include it
        elif prev_stop > stop:
            pass

        # The normal case: prev span doesn't subsume current span, so it
        # is safe to add it.
        else:
            normalized_skip_slices.append((start,stop))
            prev_start, prev_stop = start, stop

    # Now that the skip slices are sorted and there are no subsumed
    # spans, we proceed as follows.  Start with an empty list, and 
    # for each span, add the part of the list which comes before the
    # current span's start but after the previous span's stop
    censored_list = []
    prev_stop = None
    for start, stop in normalized_skip_slices:
        censored_list.extend(list_obj[prev_stop:start])
        prev_stop = stop

    censored_list.extend(list_obj[prev_stop:None])

    return censored_list







def flatten(iterable, recurse=False, depth=0):
    '''
    flattens an iterable of iterables into a simple list.  E.g.
    turns a list of list of elements into a simple list of elements.

    <recurse> will attempt to flatten the elements within the inner 
    iterable too, and will continue so long as the elements found are 
    iterable.  However, recurse will treat strings as atomic, even though
    they are iterable.
    '''

    flat_list = []
    for element in iterable:

        # If the element is not iterable, just add it to the flat list
        try:
            iter(element)
        except:
            flat_list.append(element)
            continue
        else:

            # If the element is a string, treat it as not iterable
            if isinstance(element, basestring):
                flat_list.append(element)

            # If the element is iterable and <recurse> is True, recurse
            elif recurse:
                flat_list.extend(flatten(element, recurse))

            # If the element is iterable but <recurse> is False, extend
            else:
                flat_list.extend(element)

    return flat_list



def group(iterable, num_chunks):
    '''
    Breaks <iterable> into <num_chunks> chunks (lists) of approximately 
    equal size (chunks will differ by at most one item when <num_chunks> 
    doesn't evenly divide len(<iterable>)).
    '''

    # Coerce the sequence into a list
    iterable = list(iterable)

    # Figure out the chunksize
    num_items = len(iterable)
    chunk_size = num_items / float(num_chunks)

    # Allocate approximately chunksize elements to each chunk, rounded off.
    chunks = []
    for i in range(num_chunks):
        start_index = int(math.ceil(i * chunk_size))
        end_index = int(math.ceil((i+1) * chunk_size))
        chunks.append(iterable[start_index:end_index])

    return chunks


def chunk(iterable, chunk_size):
    '''
    Returns a list of lists of items from iterable, where the internal 
    lists are each approximately of size chunk_size (except the last one,
    which is smaller if chunk_size doesn't evenly divide len(iterable)
    '''

    iterator = iter(iterable)
    chunks = []
    this_chunk = []
    still_has_items = True
    while still_has_items:
        try:
            this_chunk.append(iterator.next())
        except StopIteration:
            still_has_items = False

        if len(this_chunk) == chunk_size:
            chunks.append(this_chunk)
            this_chunk = []

        elif not still_has_items and len(this_chunk) > 0:
            chunks.append(this_chunk)

    return chunks


def rangify(iterable):
    '''
    Converts a list of indices into a list of ranges (compatible with the
    range function).  E.g. [1,2,3,7,8,9] becomes [(1,4),(7,10)].
    The iterable provided must be sorted. Duplicate indices are ignored.  
    '''
    ranges = []
    last_idx = None
    for idx in iterable:

        if last_idx is None:
            start = idx

        elif idx - last_idx > 1:
            ranges.append((start, last_idx + 1))
            start = idx

        last_idx = idx

    if last_idx is not None:
        type(ranges)
        ranges.append((start, last_idx + 1))

    return ranges




def binify(string_id, num_bins):
    ''' 
    Uniformly assign objects to one of `num_bins` bins based on the
    hash of their unique id string.
    '''
    hexdigest = hashlib.sha1(string_id).hexdigest()
    return int(hexdigest,16) % num_bins


def inbin(string_id, num_bins, this_bin):
    if this_bin >= num_bins:
        raise ValueError(
            '`this_bin` must be an integer from 0 to `num_bins`-1.')
    return binify(string_id, num_bins) == this_bin

