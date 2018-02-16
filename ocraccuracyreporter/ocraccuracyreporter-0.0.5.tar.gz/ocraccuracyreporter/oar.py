# -*- coding: utf-8 -*-

from fuzzywuzzy import fuzz as fz
import Levenshtein as lv


class oar:
    """ An OcrAccuracyReporter (oar) object has the following attributes

    label  - a meaningful name for the ocr string.
    expected - expected result
    given - result you got out of ocr pipeline

    total_expected_char_count - calculated expected char count
    total_expected_word_count - calculated expected word count

    total_given_char_count - calculated given char count
    total_given_word_count - calculated given word count

    ratio - uses pure Levenshtein Distance based matching
            (100 - means perfect match)
    partial_ratio - matches based on best substrings
    token_sort_ratio - tokenizes the strings and sorts them alphabetically

    token_set_ratio - tokenizes the strings and compared the intersection
    jaro_winkler - this algorithm giving more weight to common prefix
                   (for example, some parts are good, missing others)
    distance - this shows how many characters are really different in given
               compared to expected


    """
    label = None
    expected = None
    given = None

    # calculated values - expected
    total_expected_char_count = 0
    total_expected_word_count = 0
    # calculated values - given
    total_given_char_count = 0
    total_given_word_count = 0
    # calculated accuracy in various algorithms
    # RATIO – uses pure Levenshtein Distance based matching
    ratio = 0
    # PARTIAL_RATIO – matches based on best substrings
    partial_ratio = 0
    # TOKEN_SORT_RATIO – tokenizes the strings and sorts them alphabetically
    token_sort_ratio = 0
    # TOKEN_SET_RATIO – tokenizes the strings and compared the intersection
    token_set_ratio = 0
    # Jaro metric giving more weight to common prefix
    jaro_winkler = 0
    # this shows how many characters are really different in given compared to
    # expected
    distance = None

    def __init__(self, expected, label='', given=''):
        """required variable during class construction is 'expected'
           you can provide 'label'
           you can provide 'given'
           >>> from ocraccuracyreporter.oar import oar
           >>> oreport = oar('john', 'name', 'joh')
           if you want to just append to a csv report
           >>> print(oreport)
           >>> name,john,joh,86,100,86,86,94,1
           >>> repr(oreoprt)
           if you are creating a csv report with header info
           >>>label,expected,given,ratio,partial_ratio,token_sort_ratio,token_set_ratio,jaro_winkler,distance
              name,john,joh,86,100,86,86,94,1
         """
        # expected
        self.expected = expected.rstrip().lstrip()
        self.total_expected_char_count = len(expected)
        self.total_expected_word_count = len(expected.split())
        # any labels to associate this with.
        if label:
            self.label = label
        if given:
            self.given = given

    def __setattr__(self, name, value):

        if (name == 'given'):
            given = value.rstrip().lstrip()
            # given
            super().__setattr__('given', given)
            super().__setattr__('total_given_char_count', len(given))
            super().__setattr__('total_given_word_count', len(given.split()))
            # # calculations
            super().__setattr__('ratio', fz.ratio(self.expected, self.given))
            super().__setattr__(
                'partial_ratio', fz.partial_ratio(
                    self.expected, self.given))
            super().__setattr__(
                'token_sort_ratio',
                fz.token_sort_ratio(
                    self.expected,
                    self.given))
            super().__setattr__(
                'token_set_ratio',
                fz.token_set_ratio(
                    self.expected,
                    self.given))
            super().__setattr__(
                'jaro_winkler',
                round(lv.jaro_winkler(
                    self.expected,
                    self.given) * 100))
            super().__setattr__(
                'distance',
                lv.distance(
                    self.expected,
                    self.given))

        else:
            super().__setattr__(name, value)

    def _reportHeader(self):
        return "label,expected,given,ratio,partial_ratio,token_sort_ratio,"\
            "token_set_ratio,jaro_winkler,distance"

    # making label expected given as string
    def _reportData(self):
        return '"%s","%s","%s",%s,%s,%s,%s,%s,%s' % (self.label,
                                                     self.expected,
                                                     self.given,
                                                     self.ratio,
                                                     self.partial_ratio,
                                                     self.token_sort_ratio,
                                                     self.token_set_ratio,
                                                     self.jaro_winkler,
                                                     self.distance
                                                     )

    def __repr__(self):
        return "%s\n%s" % (self._reportHeader(), self._reportData())

    def __str__(self):
        return "%s" % (self._reportData())
