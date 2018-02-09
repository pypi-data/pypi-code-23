def get_int(track, tag):
    """Get tag from Mutagen file as an integer.

    Return the first value of a multivalued tag.  Return 1 if the tag is
    missing, empty or an invalid integer.
    """
    try:
        values = track[tag]
        # Some ID3 tags may be stored as two integers with a slash
        # (e.g. tracknumber "2/9").  Only return the first integer.
        return int(values[0].split('/')[0])
    except (IndexError, KeyError, ValueError):
        return 1


def get_str(track, tag):
    """Get tag from Mutagen file as a string.

    Return the first value of a multivalued tag.  Return '' if the tag is
    missing or empty.
    """
    try:
        values = track[tag]
        return values[0]
    except (IndexError, KeyError):
        return ''
