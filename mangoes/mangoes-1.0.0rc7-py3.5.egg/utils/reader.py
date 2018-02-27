import abc
import os.path
import re
import xml.etree.ElementTree
from collections import namedtuple

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
    lower : boolean, optional
        If True (default), converts sentences to lower case
    digit : boolean, optional
        If True (default), replace numeric values with `DIGIT_TOKEN` in sentences
    """

    def __init__(self, source, lower=False, digit=False):
        self.source = source

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
        return string.lower()

    @staticmethod
    def _digit(string):
        return re.sub(DIGIT_RE, DIGIT_TOKEN, string)

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
    FIELDS = ("form", "lemma", "POS")

    class Token(namedtuple("Token", FIELDS)):
        def lower(self):
            return self.__class__(self.form.lower(), self.lemma, self.POS)

    Token.__new__.__defaults__ = (None,) * len(FIELDS)

    def __init__(self, source, lower=False, digit=False):
        super().__init__(source, lower, digit)

    @abc.abstractmethod
    def sentences(self):
        pass


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
                sentence = []
                for token in line:
                    word, pos, lemma = token.split('/')
                    sentence.append(self.transform(self.Token(form=word, POS=pos, lemma=lemma)))
                yield sentence  # [self.transform(self.Token(*token.split('/'))) for token in line]


class XmlSentenceGenerator(AnnotatedSentenceGenerator):
    """Sentence generator for an XML source

    See Also
    --------
    :class:`SentenceGenerator`
    """
    FIELDS = ("id", "form", "lemma", "POS", "features", "head", "dependency_relation")

    class Token(namedtuple("Token", FIELDS)):
        def lower(self):
            return self.__class__(self.id, self.form.lower(), self.lemma, self.POS, self.features,
                                  self.head, self.dependency_relation)

    Token.__new__.__defaults__ = ('_',) * len(FIELDS)

    def __init__(self, source, lower=False, digit=False):
        super().__init__(source, lower, digit)

        if os.path.exists(self.source):
            self.sentences = self._sentences_from_files
        else:
            self.sentences = self._sentences_from_string

    def _parse_token(self, xml_token, dependencies=None):
        token_id, governor_id, dep_type = '_', '_', '_'
        try:
            token_id = xml_token.attrib['id']
            try:
                for dep in dependencies.findall("dep"):  # dep[dependent/@idx={}]").format(token_id)
                    if dep.find('dependent').attrib['idx'] == token_id:
                        governor_id = dep.find('governor').attrib['idx']
                        dep_type = dep.attrib['type']
                        break
            except AttributeError:
                pass
        except KeyError:
            pass

        return self.Token(id=token_id,
                          form=xml_token.find('word').text,
                          POS=xml_token.find('POS').text,
                          lemma=xml_token.find('lemma').text,
                          head=governor_id,
                          dependency_relation=dep_type)

    def _sentences_from_xml(self, xml_sentences):
        for xml_sentence in xml_sentences:
            yield [
                self.transform(self._parse_token(token, xml_sentence.find("dependencies[@type='basic-dependencies']")))
                for token in xml_sentence.iter("token")]
        raise StopIteration

    def _sentences_from_files(self):
        for xml_file in mangoes.utils.io.recursive_list_files(self.source):
            tree = xml.etree.ElementTree.parse(xml_file)
            xml_sentences = tree.getroot().iter("sentence")
            yield from self._sentences_from_xml(xml_sentences)

    def _sentences_from_string(self):
        yield from self._sentences_from_xml(xml.etree.ElementTree.fromstring(self.source).iter("sentence"))


class ConllSentenceGenerator(AnnotatedSentenceGenerator):
    """Sentence generator for source annotated in Conll format

    See Also
    --------
    :class:`SentenceGenerator`
    """
    # Stanford Conll fields = ("id", "word", "lemma", "pos", "NER", "head", "deprel")
    # Mangoes fields =        ("id", "form", "lemma", "POS", "features", "head", "dependency_relation")
    FIELDS = ("id", "form", "lemma", "POS", "NER", "head", "dependency_relation")

    class Token(namedtuple("Token", FIELDS)):
        def lower(self):
            return self.__class__(self.id, self.form.lower(), self.lemma, self.POS, self.NER,
                                  self.head, self.dependency_relation)

    def _parse_token(self, line):
        return self.Token(*line.split('\t'))

    def sentences(self):
        with mangoes.utils.io.get_reader(self.source) as reader:
            sentence = []

            for line in reader:
                line = line.strip()
                if not line:
                    yield [self.transform(token) for token in sentence]
                    sentence = []
                elif line.startswith("#"):
                    pass
                else:
                    sentence.append(self._parse_token(line))
            if sentence:
                yield [self.transform(token) for token in sentence]


class ConllUSentenceGenerator(ConllSentenceGenerator):
    # Conll U fields = ("id", "form", "lemma", "upostag", "xpostag", "feats", "head", "deprel", "deps", "misc")
    # Mangoes fields = ("id", "form", "lemma", "POS", "features", "head", "dependency_relation")

    FIELDS = ("id", "form", "lemma", "POS", "xpostag", "feats", "head", "dependency_relation", "deps", "misc")

    class Token(namedtuple("Token", FIELDS)):
        def lower(self):
            return self.__class__(self.id, self.form.lower(), self.lemma, self.POS, self.xpostag, self.feats,
                                  self.head, self.dependency_relation, self.deps, self.misc)
