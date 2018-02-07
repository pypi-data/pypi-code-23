class Word(object):
    """Store a word along with it's type.

    We create a word like this:

    >>> word = Word("fnurgle", word_type=Word.TYPE_WORD)
    >>> word
    Word('fnurgle', word_type=1)
    >>> print(word)
    fnurgle

    We can also create words of different types:

    >>> word2 = Word("http://www.github.com", Word.TYPE_URL)
    >>> word2
    Word('http://www.github.com', word_type=2)

    If we don't specify the word type, the code will try to determine
    its type on its own:

    >>> word3 = Word("http://www.github.com")
    >>> print(word3)
    http://www.github.com
    >>> word4 = Word("@enfors")
    >>> word4
    Word('@enfors', word_type=3)

    We can also do comparisons:

    >>> word5 = Word("hello")
    >>> word6 = Word("there")
    >>> word7 = Word("hello")
    >>> word5 == word6
    False
    >>> word5 == word7
    True
    """

    TYPE_WORD = 1
    TYPE_URL = 2
    TYPE_USERNAME = 3
    TYPE_TAG = 4
    TYPE_EMPTY = 5

    def __init__(self, word_text, word_type=None, keep_case=None):

        if len(word_text) == 0:
            word_type = Word.TYPE_EMPTY
        elif word_type is None:
            if "://" in word_text:
                word_type = Word.TYPE_URL
            elif word_text[0] == "@":
                word_type = Word.TYPE_USERNAME
                if keep_case is None:
                    keep_case = True
            elif word_text[0] == "#":
                word_type = Word.TYPE_TAG
            else:
                word_type = Word.TYPE_WORD

        if keep_case is not True:
            word_text = word_text.lower()

        self.word_text = word_text
        self.word_type = word_type

    def __repr__(self):
        return "Word('%s', word_type=%d)" % (self.word_text, self.word_type)

    def __str__(self):
        return self.word_text

    def __len__(self):
        return len(self.word_text)

    def __eq__(self, other_word):
        if self.word_text == other_word.word_text:
            return True
        else:
            return False
