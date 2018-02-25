import pytest

from crawlster.config import Configuration
from crawlster.validators import validate_isinstance, \
    ValidationError, one_of, is_url


@pytest.mark.parametrize('config_opts, exc_type', [
    (
            # wrong core.start_urls type
            {'core.start_urls': 'Hello there', 'core.start_step': 'test'},
            ValidationError
    )
])
def test_config_bad_init(config_opts, exc_type):
    """Exceptions are raised when invalid config is present"""
    cfg = Configuration(config_opts)
    with pytest.raises(exc_type):
        cfg.validate_options()


@pytest.mark.parametrize('config_opts', [
    # missing core.start_urls
    {'core.start_urls': ['http://example.com'], 'core.start_step': 'test'},
])
def test_config_good_init(config_opts):
    """No exception is raised on valid config"""
    cfg = Configuration(config_opts)
    cfg.validate_options()


@pytest.mark.parametrize('validator, value, fails', [
    (validate_isinstance(int), 10, False),
    (validate_isinstance(list), [1, 2, 3], False),
    (validate_isinstance(float), 100.2, False),
    (validate_isinstance(str), 10, True),
    (validate_isinstance(bool), 10, True),
    (one_of((1, 2, 3)), 3, False),
    (one_of((1, 2, 3)), 4, True),
    (one_of(('item1', 'item2', 'item3')), 'item1', False),
    (one_of(('item1', 'item2', 'item3')), 'item5', True),
    (is_url, 'http://localhost:2222/test', False),
    (is_url, 'http://localhost:2222', False),
    (is_url, 'this_is_invalid', True),
])
def test_validators(validator, value, fails):
    """Validators raise exception only on invalid values"""
    if fails:
        with pytest.raises(ValidationError):
            validator(value)
    else:
        validator(value)
