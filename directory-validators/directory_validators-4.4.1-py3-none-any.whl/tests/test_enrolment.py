from unittest import mock

from phonenumbers.phonenumberutil import NumberParseException
import pytest

from django import forms
from django.conf import settings

from directory_validators import enrolment


def create_mock_file_of_size(size):
    return mock.Mock(size=size)


def test_company_number_eight_chars_accepted():
    assert enrolment.company_number('88888888') is None
    assert enrolment.company_number('NI888888') is None


def test_company_number_seven_chars_rejected():
    with pytest.raises(forms.ValidationError):
        enrolment.company_number('8888888')


def test_company_number_nine_chars_rejected():
    with pytest.raises(forms.ValidationError):
        enrolment.company_number('888888888')


def test_logo_filesize_rejects_too_big():
    size = settings.VALIDATOR_MAX_LOGO_SIZE_BYTES + 1
    mock_file = create_mock_file_of_size(size)
    with pytest.raises(forms.ValidationError):
        enrolment.logo_filesize(mock_file)


def test_logo_filesize_accepts_not_too_big():
    size = settings.VALIDATOR_MAX_LOGO_SIZE_BYTES
    mock_file = create_mock_file_of_size(size)
    assert enrolment.logo_filesize(mock_file) is None


def test_email_domain_free_rejects_free_email():
    with pytest.raises(forms.ValidationError):
        enrolment.email_domain_free('contact@gmail.com')


def test_email_domain_free_accepts_corporate_email():
    assert enrolment.email_domain_free('contact@google.com') is None


def test_email_domain_disposable_rejects_disposable_email():
    with pytest.raises(forms.ValidationError):
        enrolment.email_domain_disposable('contact@guerillamail.com')


def test_email_domain_disposable_accepts_corporate_email():
    assert enrolment.email_domain_disposable('contact@google.com') is None


@mock.patch('phonenumbers.parse')
def test_domestic_mobile_phone_number_parse_error(mock_parse):
    mock_parse.side_effect = NumberParseException(error_type=None, msg='')
    expected_message = enrolment.MESSAGE_INVALID_PHONE_NUMBER
    with pytest.raises(forms.ValidationError) as excinfo:
        enrolment.domestic_mobile_phone_number('')
    assert expected_message in str(excinfo.value)


@mock.patch('phonenumbers.is_valid_number', mock.Mock(return_value=False))
def test_domestic_mobile_phone_number_invalid():
    expected_message = enrolment.MESSAGE_INVALID_PHONE_NUMBER
    with pytest.raises(forms.ValidationError) as excinfo:
        enrolment.domestic_mobile_phone_number('07605437499')
    assert expected_message in str(excinfo.value)


@mock.patch('phonenumbers.is_valid_number', mock.Mock(return_value=True))
def test_mobile_phone_number_valid():
    assert enrolment.domestic_mobile_phone_number('07507605384') is None


@mock.patch('phonenumbers.is_valid_number')
@mock.patch('phonenumbers.parse', return_value=mock.Mock())
@mock.patch('phonenumbers.carrier._is_mobile', mock.Mock(return_value=True))
def test_domestic_mobile_phone_number_end_to_end_call(
    mock_parse, mock_is_valid_number
):
    enrolment.domestic_mobile_phone_number('07507605483')
    mock_parse.assert_called_once_with('07507605483', 'GB')
    mock_is_valid_number.assert_called_once_with(mock_parse.return_value)


def test_domestic_mobile_phone_number_rejects_non_mobile():
    expected_message = enrolment.MESSAGE_INVALID_PHONE_NUMBER
    for value in ['+442082919192', '02082919192']:
        with pytest.raises(forms.ValidationError) as excinfo:
            enrolment.domestic_mobile_phone_number(value)
        assert expected_message in str(excinfo.value)
