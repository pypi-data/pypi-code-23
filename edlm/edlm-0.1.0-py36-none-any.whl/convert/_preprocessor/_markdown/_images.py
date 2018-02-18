# coding=utf-8
"""
Processes pictures in Markdown text
"""
import re
import typing
from pathlib import Path

from . import Context

RE_PICTURE_LINE = re.compile(r'!\['
                             r'(?P<caption>.*)'
                             r'\]'
                             r'\('
                             r'(?P<picture>.+)'
                             r'\)'
                             r'(?P<extras>.*)')

RE_WIDTH = re.compile(r'{width="(?P<width>.*)"}')
RE_WIDTH_RAW = re.compile(r'(?P<width>[\d]+)(?P<unit>.*)')


def _get_image_full_path(ctx: Context) -> str:
    image_name = Path(ctx.image_current).name
    for folder in ctx.media_folders:
        image_path = Path(folder, image_name)
        if image_path.exists():
            return str(image_path.absolute())

    raise FileNotFoundError(f'picture "{ctx.image_current}" not found in any media folders: {ctx.media_folders}')


def _get_correct_width(ctx: Context):
    match = RE_WIDTH_RAW.match(ctx.image_width_str)
    if not match:
        raise ValueError(ctx.image_width_str)

    width = int(match.group('width'))
    unit = match.group('unit')

    if unit == 'mm':
        pass
    elif unit == 'cm':
        width *= 10
    else:
        raise ValueError(unit)

    if width > ctx.image_max_width:
        ctx.debug(f'adapting width for "{ctx.image_current}" to {ctx.image_max_width}mm')
        ctx.image_width = ctx.image_max_width
    else:
        ctx.image_width = width


def _process_image_width(ctx: Context):
    width_match = RE_WIDTH.match(ctx.image_extras)

    if width_match:
        ctx.image_width_str = width_match.group('width')
        _get_correct_width(ctx)
        ctx.image_extras = RE_WIDTH.sub(f'{{width="{ctx.image_width}mm"}}', ctx.image_extras)
    else:
        ctx.image_width = ctx.image_max_width

    ctx.debug(f'setting default width for picture {ctx.image_current}')
    ctx.image_extras = f'{{width="{ctx.image_width}mm"}}'


def _process_image(ctx: Context, match) -> typing.Optional[str]:
    ctx.image_caption = match.group('caption')
    ctx.image_current = match.group('picture')
    ctx.image_extras = match.group('extras')

    _process_image_width(ctx)

    if not ctx.image_current.startswith('http'):
        ctx.debug(f'processing picture: {ctx.image_current}')
        ctx.images_used.add(Path(ctx.image_current).name)
        ctx.image_current = _get_image_full_path(ctx)

    return f'![{ctx.image_caption}]({ctx.image_current}){ctx.image_extras}'.replace('\\', '\\\\')


def process_images(ctx: Context):
    """
    Processes pictures in Markdown text

    Args:
        ctx: Context
    """
    ctx.info('processing pictures')
    ctx.images_used = set()
    output = []
    for line in ctx.markdown_text.split('\n'):
        match = RE_PICTURE_LINE.search(line)
        if match:
            output.append(RE_PICTURE_LINE.sub(_process_image(ctx, match) or line, line))
        else:
            output.append(line)

    # check_for_unused_images(ctx)

    ctx.debug('processing of pictures finished')
    ctx.markdown_text = '\n'.join(output)
