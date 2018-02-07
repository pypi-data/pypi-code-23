# coding=utf-8
from __future__ import unicode_literals

import re

PLACEHOLDER_MATCHER = re.compile('{((?:[Jj]gzs?)|(?:[Dd]e jgzs)|(?:[Hh]et jgz))}')
SUBSTITUTION_DEFAULTS = {
    'jgz': 'centrum voor Jeugd en Gezin (CJG)',
    'Jgz': 'Centrum voor Jeugd en Gezin (CJG)',
    'jgzs': 'CJG’s',
    'Jgzs': 'CJG’s',
    'de jgzs': 'de CJG’s',
    'De jgzs': 'De CJG’s',
    'het jgz': 'het Centrum voor Jeugd en Gezin (CJG)',
    'Het jgz': 'Het Centrum voor Jeugd en Gezin (CJG)'
}


def replace_jgz(article_text, substitutions=None):
    """
    Replace all JGZ placeholders in the article text with the
    appropriate strings.

    Use the optional ``substitutions`` argument to override
    any of the default substitution strings.

    """
    substitutions = substitutions or {}

    def replace(match):
        return substitutions.get(match.group(1), SUBSTITUTION_DEFAULTS.get(match.group(1)))

    return PLACEHOLDER_MATCHER.sub(replace, article_text)


ANCHOR_MATCHER = re.compile('\[a=([0-9]+),(.+?)\]')


def replace_links(article_text, replacement_callback):
    """
    Replace all internal link placeholders in the article
    text with the return value of ``replacement_callback``.

    If ``replacement_callback`` returns ``None``
    no substitution will take place.

    """
    def replace(match):
        external_id = match.group(1)
        link_text = match.group(2)
        replacement = replacement_callback(external_id, link_text)
        return match.group(0) if replacement is None else replacement

    return ANCHOR_MATCHER.sub(replace, article_text)


IMG_MATCHER = re.compile('\[img=([0-9]+)\]')


def replace_images(article_text, replacement_callback):
    """
    Replace all image placeholders in the article
    text with the return value of ``replacement_callback``.

    If ``replacement_callback`` returns ``None``
    no substitution will take place.

    """
    def replace(match):
        external_id = match.group(1)
        replacement = replacement_callback(external_id)
        return match.group(0) if replacement is None else replacement

    return IMG_MATCHER.sub(replace, article_text)


YOUTUBE_MATCHER = re.compile('\[youtube=([0-9A-z_-]+)\]')


def replace_videos(article_text, replacement_callback):
    """
    Replace all YouTube video placeholders with
    the return value of ``replacement_callback``.

    If ``replacement_callback`` returns ``None``
    no substitution will take place.

    """
    def replace(match):
        video_id = match.group(1)
        embed_url = '//www.youtube-nocookie.com/embed/{}?rel=0'.format(video_id)
        external_url = 'https://youtu.be/{}'.format(video_id)
        replacement = replacement_callback(video_id, embed_url, external_url)
        return match.group(0) if replacement is None else replacement

    return YOUTUBE_MATCHER.sub(replace, article_text)
