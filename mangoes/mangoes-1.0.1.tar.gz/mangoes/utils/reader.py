import abc
import os.path
import re
import xml.etree.ElementTree

import mangoes.utils

DIGIT_TOKEN = "0"
DIGIT_RE = r"\d+((,\d*)*(\.\d*)*)*"


class SentenceGenerator:
    """Base class for sentences generators

    A sentence generator yields sentence from a source, that can be an iterable or a set of files.

    Warnings
    --------
    This class should not be used directly.
    Use derived classes instead.

    See Also
    --------
    :class:`TextGenerator`
    :class:`BrownGenerator`
    :class:`XmlGenerator`
    :class:`ConllGenerator`

    Parameters
    ----------
    source : a string or an iterable
        An iterable of sentences or a path to a file or a repository
    filter_attributes : None or tuple, optional
        If the source is annotated, tuple or list of attributes to read. If None (default), all attributes are read.
    lower : boolean, optional
        If True (default), converts sentences to lower case
    digit : boolean, optional
        If True (default), replace numeric values with `DIGIT_TOKEN` in sentences
    """
    def __init__(self, source, lower=False, digit=False, filter_attributes=None):
        self.source = source
        self.filter_attributes = filter_attributes

        if lower and digit:
            self.transform = self._lower_and_digit
        elif lower:
            self.transform = self._lower
        elif digit:
            self.transform = self._digit
        else:
            self.transform = lambda string: string

    @staticmethod
    def _lower(string):
        try:
            return string.lower()
        except AttributeError:
            return string

    @staticmethod
    def _digit(string):
        try:
            return re.sub(DIGIT_RE, DIGIT_TOKEN, string)
        except TypeError:
            return string

    @classmethod
    def _lower_and_digit(cls, string):
        return cls._digit(cls._lower(string))

    @abc.abstractmethod
    def sentences(self):
        """Yields sentences from the source

        Yields
        -------
        list of str
        """
        pass


class TextSentenceGenerator(SentenceGenerator):
    """Sentence generator for simple text source

    See Also
    --------
    :class:`SentenceGenerator`
    """
    def __init__(self, source, lower=False, digit=False, filter_attributes=None):
        if filter_attributes:
            raise mangoes.utils.exceptions.IncompatibleValue("'text' reader can't handle annotated corpus")
        super().__init__(source, lower, digit, None)

    def sentences(self):
        with mangoes.utils.io.get_reader(self.source) as reader:
            for line in reader:
                try:
                    yield self.transform(line).split()
                except AttributeError:
                    yield [self.transform(token) for token in line]


class AnnotatedSentenceGenerator(SentenceGenerator):
    """Base class for sentences generators from annotated source

    A sentence generator yields sentence from a source, that can be an iterable or a set of files.

    Warnings
    --------
    This class should not be used directly.
    Use derived classes instead.

    See Also
    --------
    :class:`SentenceGenerator`
    """
    def __init__(self, source, lower=False, digit=False, filter_attributes=None):
        super().__init__(source, lower, digit, filter_attributes)

        if self.filter_attributes:
            self._parse_attributes = self._parse_attributes_with_filter
        else:
            self._parse_attributes = self._parse_attributes_no_filter

    def _parse_attributes_no_filter(self, token):
        return [(tag, value) for tag, value in zip(["word", "pos", "lemma"], token.split("/"))]

    def _parse_attributes_with_filter(self, token):
        return [(tag, value) for tag, value in zip(["word", "pos", "lemma"], token.split("/"))
                if tag in self.filter_attributes]

    def _format_token(self, token):
        return "/".join(["{attr[0]}:{attr[1]}".format(attr=attr) for attr in self._parse_attributes(token)])

    @abc.abstractmethod
    def sentences(self):
        pass


class XmlSentenceGenerator(AnnotatedSentenceGenerator):
    """Sentence generator for an XML source

    See Also
    --------
    :class:`SentenceGenerator`
    """
    def __init__(self, source, lower=False, digit=False, filter_attributes=None):
        super().__init__(source, lower, digit, filter_attributes)

        if os.path.exists(self.source):
            self.sentences = self._sentences_from_files
        else:
            self.sentences = self._sentences_from_string

    def _parse_attributes_no_filter(self, token):
        return [(attribute.tag, attribute.text) for attribute in token]

    def _parse_attributes_with_filter(self, token):
        return [(attribute.tag, attribute.text) for attribute in token if attribute.tag in self.filter_attributes]

    def _sentences_from_xml(self, xml_sentences):
        for xml_sentence in xml_sentences:
            yield [self.transform(self._format_token(token)) for token in xml_sentence.iter("token")]
        raise StopIteration

    def _sentences_from_files(self):
        for xml_file in mangoes.utils.io.recursive_list_files(self.source):
            tree = xml.etree.ElementTree.parse(xml_file)
            xml_sentences = tree.getroot().iter("sentence")
            yield from self._sentences_from_xml(xml_sentences)

    def _sentences_from_string(self):
        yield from self._sentences_from_xml(xml.etree.ElementTree.fromstring(self.source).iter("sentence"))


class BrownSentenceGenerator(AnnotatedSentenceGenerator):
    """Sentence generator for text source annotated in Brown format

    See Also
    --------
    :class:`SentenceGenerator`
    """
    def sentences(self):
        with mangoes.utils.io.get_reader(self.source) as reader:
            for line in reader:
                try:
                    line = line.split()
                except AttributeError:
                    pass

                yield [self.transform(self._format_token(token)) for token in line]


class ConllSentenceGenerator(AnnotatedSentenceGenerator):
    """Sentence generator for source annotated in Conll format

    See Also
    --------
    :class:`SentenceGenerator`
    """
    def sentences(self):
        with mangoes.utils.io.get_reader(self.source) as reader:
            sentence = []

            for line in reader:
                line = line.strip()
                if not line:
                    yield [self.transform(self._format_token(token)) for token in sentence]
                    sentence = []
                elif line.startswith("#"):
                    pass
                else:
                    # ex : 1	Une	une	FW	_	_	_
                    _, word, lemma, pos, *_ = line.split()
                    sentence.append("{}/{}/{}".format(word, pos, lemma))
