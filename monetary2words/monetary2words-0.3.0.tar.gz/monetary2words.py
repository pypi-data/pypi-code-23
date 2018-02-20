# -*- coding: utf-8 -*-

from float2words import float2words

currency_mapping = {
    'EUR': {
        'symbol': '€',
        'subunit_abbr': {
            # Cents
            'en': 'ct.',
            'et': 'st.',
            'lt': 'ct.',
            'lv': 'ct.',
            'pl': 'ct.',
            'ru': 'цт.',
        },
    },
    'GBP': {
        'symbol': '£',
        'subunit_abbr': {
            # Pence
            'en': 'p.',
            'et': 'p.',
            'lt': 'p.',
            'lv': 'p.',
            'pl': 'p.',
            'ru': 'п.',
        },
    },
    'PLN': {
        'symbol': 'zł',
        'subunit_abbr': {
            # Groszy
            'en': 'gr.',
            'et': 'gr.',
            'lt': 'gr.',
            'lv': 'gr.',
            'pl': 'gr.',
            'ru': 'гр.',
        },
    },
    'RUB': {
        'symbol': '₽',
        'subunit_abbr': {
            # Kopeks
            'en': 'kop.',
            'et': 'kop.',
            'lt': 'kap.',
            'lv': 'kap.',
            'pl': 'kop.',
            'ru': 'коп.',
        },
    },
    'USD': {
        'symbol': '$',
        'subunit_abbr': {
            # Cents
            'en': 'ct.',
            'et': 'st.',
            'lt': 'ct.',
            'lv': 'ct.',
            'pl': 'ct.',
            'ru': 'цт.',
        },
    },
}


def monetary2words(number, language, currency_code, connector=', ',
                   precision=2, use_symbol=True):
    """Convert monetary to words by given optional parameters.

    Arguments:
        number (float): float number.
        language (string): the code of language
            (e.g. 'en_US', 'ru_RU', 'en', 'ru', etc.).
        currency_code (string): the code of currency (e.g. 'USD', 'EUR', etc.).
        connector (string): connector will be used between whole and
            decimal parts expressed in words.
        precision (int): number of digits after decimal point.
        use_symbol (boolean): whether to use currency symbol or currency ISO
            code.

    Returns:
        number_in_words (string): monetary number in words.

    """
    if currency_code not in currency_mapping:
        raise NotImplementedError(
            "Currency code '%s' is not implemented!" % currency_code)
    currency = currency_mapping[currency_code]
    # We check if full language code is implemented and then check with first
    # two letters if it's not.
    subunit_abbr = currency['subunit_abbr']
    if language not in subunit_abbr:
        language = language[:2]
    if language not in subunit_abbr:
        raise NotImplementedError(
            "Language '%s' is not implemented for currency '%s'!" % (
                language, currency_code))
    currency_code = currency['symbol'] if use_symbol else currency_code
    return float2words(number, language, currency_code,
                       subunit_abbr[language], connector, precision)
