"""Functions to manipulate multi-track and single-track piano-rolls.

"""
from copy import deepcopy
import numpy as np
from .track import Track
from .multitrack import Multitrack

def _check_supported(obj):
    """
    Raise TypeError if the object is not a :class:`pypianoroll.Multitrack`
    or :class:`pypianoroll.Track` object. Otherwise, pass.
    """
    if not (isinstance(obj, Multitrack) or isinstance(obj, Track)):
        raise TypeError("Support only `pypianoroll.Multitrack` and "
                        "`pypianoroll.Track` class objects")

def is_pianoroll(arr):
    """
    Return True if the array is a standard piano-roll matrix. Otherwise,
    return False. Raise TypeError if the input object is not a numpy array.
    """
    if not isinstance(arr, np.ndarray):
        raise TypeError("`arr` must be of np.ndarray type")
    if not (np.issubdtype(arr.dtype, np.bool)
            or np.issubdtype(arr.dtype, np.int)
            or np.issubdtype(arr.dtype, np.float)):
        return False
    if arr.ndim != 2:
        return False
    if arr.shape[1] != 128:
        return False
    return True

def binarize(obj, threshold=0):
    """
    Return a copy of the object with binarized piano-roll(s).

    Parameters
    ----------
    threshold : int or float
        Threshold to binarize the piano-roll(s). Default to zero.
    """
    _check_supported(obj)
    copied = deepcopy(obj)
    copied.binarize(threshold)
    return copied

def clip(obj, lower=0, upper=128):
    """
    Return a copy of the object with piano-roll(s) clipped by a lower bound
    and an upper bound specified by `lower` and `upper`, respectively.

    Parameters
    ----------
    lower : int or float
        The lower bound to clip the piano-roll. Default to 0.
    upper : int or float
        The upper bound to clip the piano-roll. Default to 128.
    """
    _check_supported(obj)
    copied = deepcopy(obj)
    copied.clip(lower, upper)
    return copied

def copy(obj):
    """Return a copy of the object."""
    _check_supported(obj)
    copied = deepcopy(obj)
    return copied

def pad(obj, pad_length):
    """
    Return a copy of the object with piano-roll padded with zeros at the end
    along the time axis.

    Parameters
    ----------
    pad_length : int
        The length to pad along the time axis with zeros.
    """
    if not isinstance(obj, Track):
        raise TypeError("Support only `pypianoroll.Track` class objects")
    copied = deepcopy(obj)
    copied.pad(pad_length)
    return copied

def pad_to_same(obj):
    """
    Return a copy of the object with shorter piano-rolls padded with zeros
    at the end along the time axis to the length of the piano-roll with the
    maximal length.
    """
    if not isinstance(obj, Multitrack):
        raise TypeError("Support only `pypianoroll.Multitrack` class objects")
    copied = deepcopy(obj)
    copied.pad_to_same()
    return copied

def plot(obj, **kwargs):
    """
    Plot the object. See :func:`pypianoroll.Multitrack.plot` and
    :func:`pypianoroll.Track.plot` for full documentation.
    """
    _check_supported(obj)
    return obj.plot(**kwargs)

def transpose(obj, semitone):
    """
    Return a copy of the object with piano-roll(s) transposed by
    ``semitones`` semitones.

    Parameters
    ----------
    semitone : int
        Number of semitones to transpose the piano-roll(s).
    """
    _check_supported(obj)
    copied = deepcopy(obj)
    copied.lowest_pitch += semitone
    return copied

def trim_trailing_silence(obj):
    """
    Return a copy of the object with trimmed trailing silence of the
    piano-roll(s).
    """
    _check_supported(obj)
    copied = deepcopy(obj)
    length = copied.get_length()
    copied.pianoroll = copied.pianoroll[:length]
    return copied
