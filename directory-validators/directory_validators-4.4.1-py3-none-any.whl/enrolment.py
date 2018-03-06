import phonenumbers
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type, NumberParseException

from django.conf import settings
from django.core.validators import RegexValidator, ValidationError

from directory_validators.constants.disposable_email_domains import (
    disposable_domains
)
from directory_validators.constants.free_email_domains import free_domains
from directory_validators import helpers


MESSAGE_FILE_TOO_BIG = 'File is too big.'
MESSAGE_USE_COMPANY_EMAIL = (
    'Please use your business, company or corporate email address. We '
    'validate you as a business owner or employee through your business, '
    'company or corporate email address.'
)
MESSAGE_INVALID_PHONE_NUMBER = 'Please enter a valid UK phone number.'

company_number = RegexValidator(
    message="Company number must be 8 characters",
    regex='^[A-Za-z0-9]{8}$',  # allow alphanumeric of length 8.
    code='invalid_company_number',
)


def logo_filesize(value):
    """
    Confirms that the logo is not too large in terms of filesize.
    @param {File} value
    @returns {None}
    @raises AssertionError

    """

    if value.size > settings.VALIDATOR_MAX_LOGO_SIZE_BYTES:
        raise ValidationError(MESSAGE_FILE_TOO_BIG)


def email_domain_free(value):
    """
    Confirms that the email address is not using a free service.
    @param {str} value
    @returns {None}
    @raises AssertionError

    """

    domain = helpers.get_domain_from_email_address(value)
    if domain.lower() in free_domains:
        raise ValidationError(MESSAGE_USE_COMPANY_EMAIL)


def email_domain_disposable(value):
    """
    Confirms that the email address is not using a disposable service.
    @param {str} value
    @returns {None}
    @raises AssertionError

    """

    domain = helpers.get_domain_from_email_address(value)
    if domain.lower() in disposable_domains:
        raise ValidationError(MESSAGE_USE_COMPANY_EMAIL)


def domestic_mobile_phone_number(value):
    """
    Confirms that the phone number is a valid UK phone number.
    @param {str} value
    @returns {None}
    @raises AssertionError

    """

    try:
        parsed = phonenumbers.parse(value, 'GB')
    except NumberParseException:
        pass
    else:
        is_mobile = carrier._is_mobile(number_type(parsed))
        if is_mobile and phonenumbers.is_valid_number(parsed):
            return None
    raise ValidationError(MESSAGE_INVALID_PHONE_NUMBER)
