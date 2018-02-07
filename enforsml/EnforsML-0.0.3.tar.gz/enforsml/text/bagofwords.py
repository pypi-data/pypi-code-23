class BagOfWords(object):
    """Represents a bag of words.

    All words in the bag are automatically made lowercase.

    How to make a bag:

    >>> bag = BagOfWords(["A", "bunch", "of", "words"])

    You can add more words to an existing bag:

    >>> bag.add_words(["Some", "more", "words"])
    >>> len(bag)
    7
    """

    def __init__(self, words=None):
        """Instanciate a bag.
        """
        self.words = {}
        self.num_words = 0  # The number of non-unique words in the bag
        self.num_unique_words = 0
        if words is not None:
            self.add_words(words)

    def add_words(self, words):
        """Add words to the bag.

        >>> bag = BagOfWords("some silly old words".split(" "))
        >>> len(bag)
        4
        >>> bag.add_words("more words".split(" "))
        >>> len(bag)
        6
        >>> bag.num_unique_words
        5
        """
        for word in words:
            try:
                num = self.words[word]
            except KeyError:
                num = 0

            num = num + 1
            self.words[word] = num

        self.num_words += len(words)
        self.num_unique_words = len(self.words)

    def sorted_matrix(self, reverse=False):
        """Return a matrix with words and frequencies, sorted by
        frequency (descending).
        >>> bag = BagOfWords("some silly words".split(" "))
        >>> bag.add_words("some silly".split(" "))
        >>> bag.add_words(["some"])
        >>> for k, v in bag.sorted_matrix():
        ...     print(k, v)
        words 1
        silly 2
        some 3
        """

        matrix = [(k, self.words[k]) for k in sorted(self.words,
                                                     key=self.words.get,
                                                     reverse=reverse)]
        return matrix

    def tfidf(self, sub_corpus):
        """Calculate TF-IDF. Self is corpus.
        """
        tfidf_matrix = {}

        for word in sub_corpus.words:
            word = word.lower()
            freq = self.words[word]
            percent = freq / len(self)
            sub_freq = sub_corpus.words[word]
            sub_percent = sub_freq / len(sub_corpus)

            tfidf_matrix[word] = sub_percent / percent

#            print("\n-- word       :", word)
#            print("   freq       :", freq)
#            print("   percent    :", percent)
#            print("   sub_freq   :", sub_freq)
#            print("   sub_percent:", sub_percent)
#            print("   result     :", sub_percent / percent)

        return tfidf_matrix

    def sorted_tfidf(self, sub_corpus):
        tfidf_matrix = self.tfidf(sub_corpus)
        return [(k, tfidf_matrix[k]) for k in
                sorted(tfidf_matrix, key=tfidf_matrix.get,
                       reverse=True)]

    def __str__(self):
        """Return a human-readable string representing the bag.
        """
        return str(self.words)

    def __repr__(self):
        """Return the code needed to create this bag.
        """
        return "BagOfWords(%s)" % self.words

    def __len__(self):
        """Return the number of words in the bag.
        >>> bag = BagOfWords("some silly words".split(" "))
        >>> len(bag)
        3
        >>> bag.add_words("more words".split(" "))
        >>> len(bag)
        5
        """
        return self.num_words
