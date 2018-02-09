import functools


class InvalidSetting(Exception):
    pass


def default():
    return {
        'groups': {
            'fallback_name': 'fallback',
            'separate': {},
            'split_tags': {},
            'tags': [],
        },
        'playlist': {
            'format': 'm3u8',
            'paths': 'relative',
        },
        'tracks': {
            'blacklist': {},
            'sort': [],
        },
    }


def factory(key1, key2, val):
    if key1 == 'groups':
        return _groups(key2, val)
    if key1 == 'playlist':
        return _playlist(key2, val)
    if key1 == 'tracks':
        return _tracks(key2, val)
    raise InvalidSetting()


def merge(settings, out_settings):
    """Validate and merge settings into out_settings."""
    groups = settings.get('groups')
    if groups:
        out_groups = out_settings['groups']
        _merge_fallback_name(groups, out_groups)
        _merge_separate(groups, out_groups)
        _merge_split_tags(groups, out_groups)
        _merge_tags(groups, out_groups)

    playlist = settings.get('playlist')
    if playlist:
        out_playlist = out_settings['playlist']
        _merge_format(playlist, out_playlist)
        _merge_paths(playlist, out_playlist)

    tracks = settings.get('tracks')
    if tracks:
        out_tracks = out_settings['tracks']
        _merge_blacklist(tracks, out_tracks)
        _merge_sort(tracks, out_tracks)


def set_format(format, out_settings):
    """Set playlist format in 'out_settings' to 'format'."""
    settings = factory('playlist', 'format', format)
    merge(settings, out_settings)


def set_paths(paths, out_settings):
    """Set playlist paths in 'out_settings' to 'paths'."""
    settings = factory('playlist', 'paths', paths)
    merge(settings, out_settings)


def _key_present(key):
    """Call decorated function if 'key' is present in its first argument."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(d, *args):
            if key in d:
                func(d, *args)
        return wrapper
    return decorator


@_key_present('fallback_name')
def _merge_fallback_name(groups, out_groups):
    fallback_name = groups['fallback_name']
    if type(fallback_name) != str:
        raise InvalidSetting()

    out_groups['fallback_name'] = fallback_name


@_key_present('separate')
def _merge_separate(groups, out_groups):
    separate = groups['separate']
    _validate_common(separate)
    out_groups['separate'] = separate


@_key_present('split_tags')
def _merge_split_tags(groups, out_groups):
    split_tags = groups['split_tags']
    if type(split_tags) != dict:
        raise InvalidSetting()

    for group, tags in split_tags.items():
        if type(group) != str or type(tags) != list:
            raise InvalidSetting()

        for tag in tags:
            if type(tag) != str:
                raise InvalidSetting()

    out_groups['split_tags'] = split_tags


@_key_present('tags')
def _merge_tags(groups, out_groups):
    tags_l = groups['tags']
    if type(tags_l) != list:
        raise InvalidSetting()

    for tags in tags_l:
        if type(tags) != list:
            raise InvalidSetting()

        for tag in tags:
            if type(tag) != str:
                raise InvalidSetting()

    out_groups['tags'] = tags_l


@_key_present('format')
def _merge_format(playlist, out_playlist):
    format = playlist['format']
    if type(format) != str:
        raise InvalidSetting()

    format = format.lower()
    if format not in ('m3u8', 'pls'):
        raise InvalidSetting()

    out_playlist['format'] = format


@_key_present('paths')
def _merge_paths(playlist, out_playlist):
    paths = playlist['paths']
    if type(paths) != str:
        raise InvalidSetting()

    paths = paths.lower()
    if paths not in ('absolute', 'relative'):
        raise InvalidSetting()

    out_playlist['paths'] = paths


@_key_present('blacklist')
def _merge_blacklist(tracks, out_tracks):
    blacklist = tracks['blacklist']
    _validate_common(blacklist)
    out_tracks['blacklist'] = blacklist


@_key_present('sort')
def _merge_sort(tracks, out_tracks):
    sort = tracks['sort']
    if type(sort) != list:
        raise InvalidSetting()

    for tags in sort:
        if type(tags) != list:
            raise InvalidSetting()

        for tag in tags:
            if type(tag) != str:
                raise InvalidSetting()

    out_tracks['sort'] = sort


def _validate_common(d):
    """Validate common fields for groups.separate.* and tracks.blacklist.*."""
    if type(d) != dict:
        raise InvalidSetting()

    for group, tags_l in d.items():
        if type(group) != str or type(tags_l) != list:
            raise InvalidSetting()

        for tags_d in tags_l:
            if type(tags_d) != dict:
                raise InvalidSetting()

            for tag, val in tags_d.items():
                if type(tag) != str or type(val) != str:
                    raise InvalidSetting()


def _groups(key, val):
    if key in ('tags', 'fallback_name', 'split_tags', 'separate'):
        return {
            'groups': {
                key: val,
            },
        }
    raise InvalidSetting()


def _playlist(key, val):
    if key in ('format', 'paths'):
        return {
            'playlist': {
                key: val,
            },
        }
    raise InvalidSetting()


def _tracks(key, val):
    if key in ('sort', 'blacklist'):
        return {
            'tracks': {
                key: val,
            },
        }
    raise InvalidSetting()
