import pytest
from django.core.exceptions import ValidationError

from directory_validators import password_validation


@pytest.mark.parametrize(
    'password',
    ('', '12ab', '123', '%£$K')
)
def test_alphabetic_password_validator(password):
    validator = password_validation.AlphabeticPasswordValidator()
    assert validator.validate(password=password) is None
    assert validator.get_help_text() == \
        password_validation.ALPHABETIC_HELP_TEXT


@pytest.mark.parametrize(
    'password',
    ('abc', 'AbC', 'ABC')
)
def test_alphabetic_password_validator_exception_raised(password):
    validator = password_validation.AlphabeticPasswordValidator()
    with pytest.raises(ValidationError) as e:
        validator.validate(password=password)
    assert password_validation.ALPHABETIC_VALIDATION_MESSAGE in str(e.value)


@pytest.mark.parametrize(
    'password',
    ('foobar', '12ab', '123', '%£$K')
)
def test_common_word_password_validator(password):
    validator = password_validation.PasswordWordPasswordValidator()
    assert validator.validate(password=password) is None
    assert validator.get_help_text() == \
        password_validation.PASSWORD_WORD_HELP_TEXT


@pytest.mark.parametrize(
    'password',
    (
        'password',
        'PASSWORD',
        'PaSsWord',
        'FooPasswordBar',
        'foobarpassWord',
        'barPASSWORD',
        'passwordpassword'
    )
)
def test_common_word_validator_exception_raised(password):
    validator = password_validation.PasswordWordPasswordValidator()
    with pytest.raises(ValidationError) as e:
        validator.validate(password=password)
    assert password_validation.PASSWORD_WORD_VALIDATION_MESSAGE in str(e.value)
