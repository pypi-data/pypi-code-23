from directory_validators import helpers


def test_tokenize_keywords_trailing_spaces():
    actual = helpers.tokenize_keywords('really good, nice, great and good')
    assert actual == ['really good', 'nice', 'great and good']


def test_tokenize_keywords_leading_spaces():
    actual = helpers.tokenize_keywords(' really good ,nice ,great and good ')
    assert actual == ['really good', 'nice', 'great and good']


def test_tokenize_keywords_no_spaces():
    actual = helpers.tokenize_keywords('really good,nice,great and good')
    assert actual == ['really good', 'nice', 'great and good']


def test_tokenize_keywords_trailing_comma():
    actual = helpers.tokenize_keywords('really good,nice,great and good,')
    assert actual == ['really good', 'nice', 'great and good']


def test_tokenize_keywords_trailing_comma_space():
    actual = helpers.tokenize_keywords('really good,nice,great and good, ')
    assert actual == ['really good', 'nice', 'great and good']
