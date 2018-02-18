# coding=utf-8

from pathlib import Path

from edlm.convert import Context
from edlm.convert._get_media_folders import get_media_folders

# def test_not_media_folder():
#     ctx = Context()
#     ctx.source_folder = Path('.').absolute()
#     with pytest.raises(ConvertError):
#         get_media_folders(ctx)


def test_get_media_folder():
    ctx = Context()
    ctx.source_folder = Path('.').absolute()
    media = Path('./media').absolute()
    media.mkdir()
    get_media_folders(ctx)
    assert ctx.media_folders == [media]


def test_get_media_folder_multiple():
    sub1 = Path('./sub1').absolute()
    sub1.mkdir()
    media1 = Path(sub1, 'media').absolute()
    media1.mkdir()
    sub2 = Path(sub1, 'sub2').absolute()
    sub2.mkdir()
    media2 = Path(sub2, 'media').absolute()
    media2.mkdir()
    sub3 = Path(sub2, 'sub3').absolute()
    sub3.mkdir()
    media3 = Path(sub3, 'media').absolute()
    media3.mkdir()
    ctx = Context()
    ctx.source_folder = sub3
    get_media_folders(ctx)
    assert ctx.media_folders == [media3, media2, media1]
