# -*- coding: utf-8 -*-
""" Class to manage the words to be represented in embeddings or used as contexts.

"""

import logging
import os.path
import json
import collections

import mangoes.utils.decorators
import mangoes.utils.exceptions
from mangoes.constants import ENCODING

_logger = logging.getLogger(__name__)


class Vocabulary:
    """List of words.

    Vocabulary encapsulates a mapping between words and their ids.
    A Vocabulary can be create from a collection of words.

    Parameters
    ----------
    source: list or dict
        List of words or dict where keys are words and values are their indices

    language: str (optional)

    entity: str or tuple (optional)
        if the words are annotated, attribute(s) of each word

    See Also
    ---------
    :func:`mangoes.corpus.Corpus.create_vocabulary`
    """

    FILE_HEADER_PREFIX = "_$"

    def __init__(self, source, language="en", entity=None):
        self._params = {"language": language, "entity": entity}

        self._index_word = []
        self.word_index = {}
        self._factory(source)

    def __len__(self):
        return len(self._index_word)

    def __eq__(self, other):
        return self._index_word == other._index_word

    def __ne__(self, other):
        return not self.__eq__(other)

    def __iter__(self):
        return self._index_word.__iter__()

    def __contains__(self, word):
        return word in self.word_index

    def __getitem__(self, index):
        return self._index_word[index]

    @property
    def language(self):
        return self._params["language"]

    @property
    def entity(self):
        return self._params["entity"]

    @property
    def params(self):
        return self._params

    @property
    def words(self):
        """Returns the words of the vocabulary as a list"""
        return self._index_word

    def get_bigrams(self):
        # TODO : temporary fix. Define bigrams of tuples
        return [w for w in self.words if ' ' in w or (isinstance(w, tuple) and isinstance(w[0], tuple) and len(w) == 2)]

    def index(self, word):
        """Returns the index associated to the word"""
        return self.word_index[word]

    def indices(self, sentence):
        """Convert words of the sentence to indices

        If a word isn't in the vocabulary, its index is replaced with -1

        Parameters
        ----------
        sentence: list of str

        Returns
        -------
        list of int
        """
        return [self.index(word) if word in self else -1 for word in sentence]

    def save(self, path, name="vocabulary"):
        """Save the vocabulary in a file.

        Parameters
        ----------
        path: str
            Local path to the directory where vocabulary should be written

        name: str
            Name of the file to create (without extension)

        Warnings
        ---------
        If the file already exists, it will be overwritten.
        """

        file_path = os.path.join(path, name + '.txt')
        with open(file_path, "w", encoding=ENCODING) as f:
            f.write(self.FILE_HEADER_PREFIX + json.dumps({k: v for k, v in self._params.items() if v},
                                                         allow_nan=False) + "\n")
            f.write("\n".join([str(w) for w in self._index_word]))
        return file_path

    @classmethod
    def load(cls, path, name):
        """Load the vocabulary from its associated file.

        Parameters
        -----------
        path: str
            Local path to the directory where vocabulary file is located

        name: str
            Name of the file (without extension)

        Returns
        --------
        Vocabulary
        """
        temp_words = []
        params = {}
        with open(os.path.join(path, name + '.txt'), "r", encoding=ENCODING) as f:
            first_line = f.readline()
            if first_line.startswith(cls.FILE_HEADER_PREFIX):
                params = json.loads(first_line[len(cls.FILE_HEADER_PREFIX):].strip())
            else:
                f.seek(0)

            for word in f:
                temp_words.append(word.strip())

        return Vocabulary(temp_words, **params)

    def _factory(self, words):
        if isinstance(words, self.__class__):
            self._params = words._params
            self._from_list(words._index_word)
        elif isinstance(words, dict):
            self._from_dict(words)
        elif isinstance(words, list):
            self._from_list(words)
        else:
            try:
                self._from_list(words.words)
            except:
                error_message = "{} can't be used as input to create a Vocabulary. " \
                                "A Vocabulary, a dict or a list is expected".format(type(words))
                raise mangoes.utils.exceptions.UnsupportedType(error_message)

    def _from_dict(self, word_index):
        words_list = sorted(word_index, key=word_index.get)
        self._from_list(words_list)

    def _from_list(self, words):
        self._index_word = words
        self.word_index = {word: index for index, word in enumerate(self._index_word)}


class DynamicVocabulary(Vocabulary):
    """Extensible list of words.

    A DynamicVocabulary can be created from a collection of words or empty and each new encountered word will be
    added to it either explicitly (with :func:`.add()` or implicitly when testing if the word is in the vocabulary
    (always returns True) or getting its index

    Examples
    --------
    >>> v = mangoes.vocabulary.DynamicVocabulary()
    >>> print(v.words)
    []
    >>> v.add('a')
    0
    >>> print(v.words)
    ['a']
    >>> 'b' in v
    True
    >>> v.index('b')
    1
    >>> v.index('c')
    2


    Parameters
    ----------
    source: list or dict (optional)
        List of words or dict where keys are words and values are their indices

    language: str (optional)

    entity: str or tuple (optional)
        if the words are annotated, attribute(s) of each word

    See Also
    ---------
    :func:`mangoes.corpus.Corpus.create_vocabulary`
    """
    def __init__(self, source=None, *args, **kwargs):
        if not source:
            source = []
        super().__init__(source, *args, **kwargs)

    def add(self, word):
        if word not in self.word_index:
            self.word_index[word] = len(self.words)
            self.words.append(word)
        return self.word_index[word]

    def index(self, word):
        """Returns the index associated to the word, adding it to the vocabulary if not yet"""
        try:
            return self.word_index[word]
        except KeyError:
            return self.add(word)

    def __contains__(self, word):
        self.add(word)
        return True


def create_token_filter(fields):
    """Returns a function to filter the given fields from a token

    Examples
    --------
    >>> Token = mangoes.corpus.BROWN.Token
    >>> cat_token = Token(form="cat", lemma="cat", POS="NOUN")
    >>> mangoes.vocabulary.create_token_filter("lemma")(cat_token)
    'cat'
    >>> mangoes.vocabulary.create_token_filter(("lemma", "POS"))(cat_token)
    Token(lemma='cat', POS='NOUN')

    Parameters
    ----------
    fields: str or tuple
        name of the fields(s) to keep

    Returns
    -------
    callable


    """
    if fields:
        if isinstance(fields, str):
            def filter_token(token):
                if getattr(token, '_fields', None):
                    # the token is a single Token
                    return getattr(token, fields)
                elif isinstance(token, tuple) and len(token) == 2:
                    # the token is a bigram (tuple of Tokens
                    return (getattr(token[0], fields), getattr(token[1], fields))
                else:
                    raise NotImplementedError
        else:
            from collections import namedtuple
            Token = namedtuple('Token', fields)

            def filter_token(token):
                if getattr(token, '_fields', None):
                    # the token is a single Token
                    return Token(*[getattr(token, attr) for attr in fields])
                elif isinstance(token, tuple) and len(token) == 2:
                    # the token is a bigram (tuple of Tokens
                    return (Token(*[getattr(token[0], attr) for attr in fields]),
                            Token(*[getattr(token[1], attr) for attr in fields]))
                else:
                    raise NotImplementedError
    else:
        def filter_token(token):
            return token
    return filter_token


def create_tokens_filter(fields):
    """Returns a function to filter the given fields from a list of tokens"""
    if fields:
        filter_token = create_token_filter(fields)

        def filter_tokens(sentence):
            return [filter_token(token) for token in sentence]
    else:
        def filter_tokens(sentence):
            return sentence

    return filter_tokens


def create_bigrams_filter(bigrams=None, annotated=False):
    """Returns a function to filter the given fields from a list of tokens"""
    # TODO : deal with Tokens
    if bigrams:
        if annotated:

            # Token = collections.namedtuple('Token', bigrams[0][0]._fields)
            fields = bigrams[0][0]._fields
            Token = collections.namedtuple('Token', fields)

            def filter_bigrams(sentence):
                filtered_sentence = []
                i = 0
                while i < len(sentence):
                    try:
                        x = (Token(*[getattr(sentence[i], f) for f in fields]), Token(*[getattr(sentence[i + 1], f) for f in fields]))
                        if x in bigrams:
                            filtered_sentence.append((sentence[i], sentence[i + 1]))
                            i += 1
                        else:
                            filtered_sentence.append(sentence[i])
                    except IndexError:
                        # sentence[i] or sentence[i + 1] is None
                        filtered_sentence.append(sentence[i])
                    i += 1
                return filtered_sentence
        else:
            def filter_bigrams(sentence):
                filtered_sentence = []
                i = 0
                while i < len(sentence):
                    try:
                        if sentence[i] + ' ' + sentence[i + 1] in bigrams:
                            filtered_sentence.append(sentence[i] + ' ' + sentence[i + 1])
                            i += 1
                        else:
                            filtered_sentence.append(sentence[i])
                    except (TypeError, IndexError):
                        # sentence[i] or sentence[i + 1] is None
                        filtered_sentence.append(sentence[i])
                    i += 1
                return filtered_sentence
    else:
        def filter_bigrams(sentence):
            return sentence

    return filter_bigrams





