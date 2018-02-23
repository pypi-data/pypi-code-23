# coding=utf-8

from pathlib import Path

import elib
import pytest
from hypothesis import given
from hypothesis import strategies as st
from mockito import mock, verify, when

import edlm.convert._preprocessor._markdown._images as image
from edlm.convert import Context
from edlm.convert._check_for_unused_images import check_for_unused_images


@pytest.fixture(name='media')
def _dummy_media_folder():
    media = Path('./media')
    media.mkdir()
    test_files = [Path(f'./media/{elib.custom_random.random_string()}') for _ in range(10)]
    for file in test_files:
        file.touch()
    yield media


def test_get_image_full_path():
    test_file = Path('./test.png')
    test_file.touch()
    ctx = Context()
    ctx.media_folders = [Path('.')]
    ctx.image_current = test_file.name
    assert image._get_image_full_path(ctx) == str(test_file.absolute())


def test_image_doesnt_exist():
    ctx = Context()
    ctx.media_folders = [Path('.')]
    ctx.image_current = Path('./nope').name
    with pytest.raises(FileNotFoundError):
        image._get_image_full_path(ctx)


@given(width_str=st.from_regex(r'^[\d]{1,5}(cm|mm)$'))
def test_get_correct_width(width_str):
    ctx = Context()
    ctx.image_width_str = width_str
    ctx.image_max_width = 300
    image._get_correct_width(ctx)
    assert ctx.image_width <= 300


def test_get_correct_width_wrong_unit():
    ctx = Context()
    ctx.image_width_str = '9pm'
    ctx.image_max_width = 300
    with pytest.raises(ValueError):
        image._get_correct_width(ctx)


def test_shrink():
    ctx = Context()
    ctx.image_width_str = '50cm'
    ctx.image_max_width = 20
    image._get_correct_width(ctx)
    assert ctx.image_width == 20


def test_get_correct_width_wrong_raw_str():
    ctx = Context()
    ctx.image_width_str = 'x9pm'
    with pytest.raises(ValueError) as exc:
        image._get_correct_width(ctx)
        assert 'x9pm' in exc


def test_process_image_width_no_width_given():
    ctx = Context()
    ctx.image_max_width = 100
    ctx.image_extras = ''
    image._process_image_width(ctx)
    assert ctx.image_extras == '{width="100mm"}'


def test_process_image_width():
    ctx = Context()
    ctx.image_max_width = 200
    ctx.image_extras = '{width="10cm"}'
    image._process_image_width(ctx)
    assert ctx.image_extras == '{width="100mm"}'


def test_check_for_unused_images(caplog, media: Path):
    caplog.set_level(30, 'EDLM')
    caplog.clear()
    ctx = Context()
    ctx.media_folders = [str(media.absolute()), '.']
    ctx.images_used = set()
    check_for_unused_images(ctx)
    for file in media.iterdir():
        assert file.name in caplog.text


def test_check_for_used_images(caplog, media: Path):
    caplog.set_level(30, 'EDLM')
    caplog.clear()
    ctx = Context()
    ctx.media_folders = [str(media.absolute()), '.']
    ctx.images_used = set()
    caplog.clear()
    ctx.images_used = set()
    for file in list(media.iterdir())[5:]:
        ctx.images_used.add(file.name)
    check_for_unused_images(ctx)
    for file in list(media.iterdir())[:5]:
        assert file.name in caplog.text
    for file in list(media.iterdir())[5:]:
        assert file.name not in caplog.text


def test_check_for_no_unused_images(caplog, media: Path):
    caplog.set_level(30, 'EDLM')
    caplog.clear()
    ctx = Context()
    ctx.media_folders = [str(media.absolute()), '.']
    ctx.images_used = set()
    caplog.clear()
    ctx.images_used = set()
    for file in list(media.iterdir()):
        ctx.images_used.add(file.name)
    check_for_unused_images(ctx)
    for file in list(media.iterdir()):
        assert file.name not in caplog.text


def test_check_for_used_images_only_one_media_folder(caplog):
    caplog.set_level(30, 'EDLM')
    caplog.clear()
    ctx = Context()
    ctx.media_folders = ['.']
    ctx.images_used = set()
    check_for_unused_images(ctx)
    assert not caplog.text


def test_process_image():
    ctx = Context()
    ctx.images_used = set()
    match = mock()
    when(match).group('caption').thenReturn('caption')
    when(match).group('picture').thenReturn('.')
    when(match).group('extras').thenReturn('extras')
    when(image)._process_image_width(ctx)
    when(image)._get_image_full_path(ctx).thenReturn('image_current')

    result = image._process_image(ctx, match)
    assert result == '![caption](image_current)extras'

    assert ctx.image_current == 'image_current'
    verify(image)._process_image_width(ctx)
    when(image)._get_image_full_path(ctx)


def test_process_image_http():
    ctx = Context()
    ctx.images_used = set()
    match = mock()
    when(match).group('caption').thenReturn('caption')
    when(match).group('picture').thenReturn('http://something')
    when(match).group('extras').thenReturn('extras')
    when(image)._process_image_width(ctx)
    when(image)._get_image_full_path(ctx).thenReturn('image_current')

    result = image._process_image(ctx, match)
    assert result == '![caption](http://something)extras'

    assert ctx.image_current == 'http://something'
    verify(image)._process_image_width(ctx)
    when(image)._get_image_full_path(ctx)


def test_process_images(media):
    ctx = Context()
    ctx.image_max_width = 200
    ctx.media_folders = [str(media.absolute()), '.']
    pictures = list(media.iterdir())
    ctx.markdown_text = f"""
![picture1](http://picture1.com)
![picture2]({pictures[0].name})
    ![picture3](http://picture1.com)
    """
    image.process_images(ctx)
    print(ctx.markdown_text)
    assert ctx.markdown_text == f"""
![picture1](http://picture1.com){{width="200mm"}}
![picture2]({pictures[0].absolute()}){{width="200mm"}}
    ![picture3](http://picture1.com){{width="200mm"}}
    """
