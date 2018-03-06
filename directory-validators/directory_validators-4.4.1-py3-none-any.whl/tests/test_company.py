from io import BytesIO
from unittest import mock

import pytest
from PIL import (
    Image, ImageDraw, PngImagePlugin, JpegImagePlugin, GifImagePlugin
)

from django import forms
from django.conf import settings

from directory_validators import company


def create_test_image(extension):
    image = Image.new("RGB", (300, 50))
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), "This text is drawn on image")
    byte_io = BytesIO()
    image.save(byte_io, extension)
    byte_io.seek(0)
    return byte_io


def create_mock_file_of_size(size):
    return mock.Mock(size=size)


@pytest.fixture(scope='session')
def gif_image():
    return GifImagePlugin.GifImageFile(create_test_image('gif'))


@pytest.fixture(scope='session')
def png_image():
    return PngImagePlugin.PngImageFile(create_test_image('png'))


@pytest.fixture(scope='session')
def jpeg_image():
    return JpegImagePlugin.JpegImageFile(create_test_image('jpeg'))


def test_image_format_invalid_format(gif_image):
    with pytest.raises(forms.ValidationError):
        company.image_format(mock.Mock(image=gif_image))


def test_image_format_valid_format(png_image, jpeg_image):
    for image in (jpeg_image, png_image):
        assert company.image_format(mock.Mock(image=image)) is None


def test_case_study_image_filesize_rejects_too_big():
    size = settings.VALIDATOR_MAX_CASE_STUDY_IMAGE_SIZE_BYTES + 1
    mock_file = create_mock_file_of_size(size)
    expected_message = company.MESSAGE_FILE_TOO_BIG
    with pytest.raises(forms.ValidationError) as excinfo:
        company.case_study_image_filesize(mock_file)
    assert expected_message in str(excinfo.value)


def test_case_study_image_filesize_accepts_not_too_big():
    size = settings.VALIDATOR_MAX_CASE_STUDY_IMAGE_SIZE_BYTES
    mock_file = create_mock_file_of_size(size)
    assert company.case_study_image_filesize(mock_file) is None


def test_case_study_video_filesize_rejects_too_big():
    size = settings.VALIDATOR_MAX_CASE_STUDY_VIDEO_SIZE_BYTES + 1
    mock_file = create_mock_file_of_size(size)
    expected_message = company.MESSAGE_FILE_TOO_BIG
    with pytest.raises(forms.ValidationError) as excinfo:
        company.case_study_video_filesize(mock_file)
    assert expected_message in str(excinfo.value)


def test_case_study_video_filesize_accepts_not_too_big():
    size = settings.VALIDATOR_MAX_CASE_STUDY_VIDEO_SIZE_BYTES
    mock_file = create_mock_file_of_size(size)
    assert company.case_study_video_filesize(mock_file) is None


def test_case_study_social_link_facebook_accepts_schemes():
    expected_legal_urls = [
        'https://facebook.com/thing',
        'http://facebook.com/thing',
    ]
    for url in expected_legal_urls:
        assert company.case_study_social_link_facebook(url) is None


def test_case_study_social_link_facebook_accepts_subdomains():
    expected_legal_urls = [
        'http://thing.facebook.com/thing',
        'http://www.facebook.com/thing',
    ]
    for url in expected_legal_urls:
        assert company.case_study_social_link_facebook(url) is None


def test_case_study_social_link_facebook_rejects_wrong_service():
    url = 'http://google.com'
    expected_message = company.MESSAGE_NOT_FACEBOOK
    with pytest.raises(forms.ValidationError) as excinfo:
        company.case_study_social_link_facebook(url)
    assert expected_message in str(excinfo.value)


def test_case_study_social_link_twitter_accepts_schemes():
    expected_legal_urls = [
        'https://twitter.com/thing',
        'http://twitter.com/thing',
    ]
    for url in expected_legal_urls:
        assert company.case_study_social_link_twitter(url) is None


def test_case_study_social_link_twitter_accepts_subdomains():
    expected_legal_urls = [
        'http://thing.twitter.com/thing',
        'http://www.twitter.com/thing',
    ]
    for url in expected_legal_urls:
        assert company.case_study_social_link_twitter(url) is None


def test_case_study_social_link_twitter_rejects_wrong_service():
    url = 'http://google.com'
    expected_message = company.MESSAGE_NOT_TWITTER
    with pytest.raises(forms.ValidationError) as excinfo:
        company.case_study_social_link_twitter(url)
    assert expected_message in str(excinfo.value)


def test_case_study_social_link_linkedin_accepts_schemes():
    expected_legal_urls = [
        'https://linkedin.com/thing',
        'http://linkedin.com/thing',
    ]
    for url in expected_legal_urls:
        assert company.case_study_social_link_linkedin(url) is None


def test_case_study_social_link_linkedin_accepts_subdomains():
    expected_legal_urls = [
        'http://thing.linkedin.com/thing',
        'http://www.linkedin.com/thing',
    ]
    for url in expected_legal_urls:
        assert company.case_study_social_link_linkedin(url) is None


def test_case_study_social_link_linkedin_rejects_wrong_service():
    url = 'http://google.com'
    expected_message = company.MESSAGE_NOT_LINKEDIN
    with pytest.raises(forms.ValidationError) as excinfo:
        company.case_study_social_link_linkedin(url)
    assert expected_message in str(excinfo.value)


@pytest.mark.parametrize('value', [
    'thing <a href="#">',
    '<a onmouseover=javascript:func()>stuff</a>'
])
def test_no_html_invalid(value):
    expected_message = company.MESSAGE_REMOVE_HTML
    with pytest.raises(forms.ValidationError) as excinfo:
        company.no_html(value)
    assert expected_message in str(excinfo.value)


@pytest.mark.parametrize('value', [
    'thing',
    'thing 1 < 2',
    'thing 1 <2',
    'thing 1<2',
    'thing 1<2>3',
    'thing 1<2 >3',
    'thing 1<2 > 3',
])
def test_no_html_valid(value):
    assert company.no_html(value) is None


@pytest.mark.parametrize('value', [
    'RC000304',
    'rc000304'
])
def test_no_royal_charter_invalid(value):
    with pytest.raises(forms.ValidationError):
        company.no_royal_charter(value)


def test_no_royal_charter_valid():
    assert company.no_royal_charter('99000304') is None
