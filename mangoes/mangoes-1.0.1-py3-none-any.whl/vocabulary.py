# -*- coding: utf-8 -*-
""" Class to manage the words to be represented in embeddings or used as contexts.

"""

import logging
import os.path
import json

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
        self._logger = logging.getLogger("{}.{}".format(__name__, self.__class__.__name__))

        self._params = {"language": language, "entity": entity}

        self._index_word = []
        self.word_index = {}
        self._factory(source)

    def __len__(self):
        return len(self._index_word)

    def __eq__(self, other):
        return self._index_word == other

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

    def index(self, word):
        """Returns the index associated to the word"""
        return self.word_index[word]

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
            f.write("\n".join(self._index_word))
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
            error_message = "{} can't be used as input to create a Vocabulary. " \
                            "A Vocabulary, a dict or a list is expected".format(type(words))
            raise mangoes.utils.exceptions.UnsupportedType(error_message)

    def _from_dict(self, word_index):
        words_list = sorted(word_index, key=word_index.get)
        self._from_list(words_list)

    def _from_list(self, words):
        self._index_word = words
        self.word_index = {word: index for index, word in enumerate(self._index_word)}
