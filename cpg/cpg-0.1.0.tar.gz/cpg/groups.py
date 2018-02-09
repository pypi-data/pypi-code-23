import glob
import random

import click
import mutagen

from . import tag


def create(audio_dir, settings):
    """Scan directory for audio files and return a list of groups.

    Scan the passed music directory for audio files, assign the audio files to
    groups, sort each group's tracks and randomly shuffle the groups.  Return
    the groups as a list.
    """
    groups = {}

    for path in _find_music(audio_dir):
        try:
            track = mutagen.File(path, easy=True)
        except mutagen.MutagenError as e:
            click.echo(e, err=True)
            continue

        tag_val = _group_tag_val(settings, track)
        tracks = groups.setdefault(tag_val, [])
        tracks.append(track)

    _remove_blacklisted(groups, settings)
    groups = _split_groups(groups, settings)
    groups = _separate_groups(groups, settings)
    _sort_tracks(groups, settings)
    groups = list(groups.items())
    random.shuffle(groups)

    return groups


def _find_music(path):
    paths = []
    for ext in ('flac', 'mp3', 'ogg'):
        paths += glob.glob(f'{path}/**/*.{ext}', recursive=True)
    return paths


def _group_tag_val(settings, track):
    for tags in settings['groups']['tags']:
        vals = []

        for t in tags:
            val = tag.get_str(track, t)
            if val == '':
                break
            vals.append(val)
        else:
            return '\t'.join(vals)

    return settings['groups']['fallback_name']


def _remove_blacklisted(groups, settings):
    """Remove blacklisted tracks from groups according to settings."""
    for group, tags_l in settings['tracks']['blacklist'].items():
        try:
            tracks = groups[group]
        except KeyError:
            continue

        new_tracks = []
        for track in tracks:
            if not _blacklisted(track, tags_l):
                new_tracks.append(track)
        groups[group] = new_tracks


def _blacklisted(track, tags_l):
    """Return whether 'track' is blacklisted by tags in 'tags_l'.

    'track' is a Mutagen file.  'tags_l' is a list of dicts which map tag names
    to tag values.
    """
    for tags_d in tags_l:
        if _tags_match(track, tags_d):
            return True
    return False


def _tags_match(track, tags_d):
    """Return whether 'track' contains tags as specified by 'tags_d'.

    'track' is a Mutagen file.  Dict 'tags_d' maps tag names to tag values.
    """
    for t, val in tags_d.items():
        if tag.get_str(track, t) != val:
            return False
    return True


def _split_groups(groups, settings):
    split_tags = settings['groups']['split_tags']
    if not split_tags:
        return groups

    new_groups = {}
    for group, tracks in groups.items():
        try:
            tags = split_tags[group]
        except KeyError:
            new_groups[group] = tracks
            continue

        for track in tracks:
            vals = [group]
            for t in tags:
                val = tag.get_str(track, t)
                if val:
                    vals.append(val)
            new_group = '\t'.join(vals)
            new_tracks = new_groups.setdefault(new_group, [])
            new_tracks.append(track)

    return new_groups


def _separate_groups(groups, settings):
    separate = settings['groups']['separate']
    if not separate:
        return groups

    new_groups = {}
    for group, tracks in groups.items():
        try:
            tags_l = separate[group]
        except KeyError:
            new_groups[group] = tracks
            continue

        for track in tracks:
            matches = False
            for tags_d in tags_l:
                for t, val in tags_d.items():
                    if tag.get_str(track, t) != val:
                        break
                else:
                    matches = True
                    break

            if matches:
                vals = [group]
                for tags_d in tags_l:
                    vals += tags_d.values()
                new_group = '\t'.join(vals)
            else:
                new_group = group
            new_tracks = new_groups.setdefault(new_group, [])
            new_tracks.append(track)

    return new_groups


def _sort_tracks(groups, settings):
    sort = settings['tracks']['sort']
    if not sort:
        return

    for tracks in groups.values():
        sort_tags = None
        for tags in sort:
            if _all_tags_set(tags, tracks):
                sort_tags = tags
                break
        if not sort_tags:
            continue

        for t in sort_tags:
            if t in ('tracknumber', 'discnumber'):  # TODO: add more tags.
                tracks.sort(key=lambda track: tag.get_int(track, t))
            else:
                tracks.sort(key=lambda track: tag.get_str(track, t))


def _all_tags_set(tags, tracks):
    """Return whether every passed tag is set in the passed tracks."""
    if not tracks or not tags:
        return True

    for track in tracks:
        for t in tags:
            if not tag.get_str(track, t):
                return False

    return True
