# *- encoding: utf-8 -*-
"""
Author: Jared Wilber

This script contains a class, "TextCleaner", used for cleaning text data.

The class is purposely a child to sklearn's BaseEstimator and TransformerMixin for two reasons:
    1. This allows us to use the class in sklearn Pipelines
    2. This provides the familiar sklearn API with methods such as 'fit' and 'transform'.


Example Code
-------------
>> preprocessor = TextCleaner()
>> preprocessor.fit(data)
>> cleaned_data = preprocessor.transform([data])
"""
from sklearn.base import BaseEstimator, TransformerMixin


class TextCleaner(BaseEstimator, TransformerMixin):
    """
    Custom sklearn transformer to preprocess data.
    Data fit to should be raw document (not split by tokens).
    """

    def __init__(self, remove_stopwords=True, do_lemmatize=False, do_stem=False, stop_words=None, return_list=True):
        """
        Parameters
        ----------
        remove_stopwords: Boolean
            Whether or not to remove stopwords.
        do_lemmatize: Boolean
            Whether or not to lemmatize tokens.
        do_stem: Boolean
            Whether or not to stem tokens.
        stop_words: iterable
            List of stop words, each word of type str.
        return_list: Boolean
            Whether or not to return list or raw document.
            Some sklearn vectorizers prefer a raw document.

        Note - if neither `do_lemmatize` nor `do_stem` are specified, the transform
        method will preprocess using `fast_process`, which is much faster.
        """
        from nltk.corpus import stopwords
        from nltk.stem import PorterStemmer, WordNetLemmatizer

        if stop_words:
            self.stopwords = set(stop_words)
        else:
            self.stopwords = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.stemmer = PorterStemmer()
        self.do_lemmatize = do_lemmatize
        self.do_stem = do_stem
        self.remove_stopwords = remove_stopwords
        # if not stemming or lemmatizing, use faster preprocessing
        if do_lemmatize or do_stem:
            self.preprocess = self.process
        else:
            self.preprocess = self.fast_process
        self.return_list = return_list

    def stem(self, token):
        """
        Stems word `token` via nltk's PorterStemmer.
        """
        return self.stemmer.stem(token)

    def lemmatize(self, token, pos_tag):
        """
        Lemmatizes token via nltk's WordNetLemmatizer.
        This method bust be called on a tuple of (token, post_tag).

        Parameters
        ----------
        token : str
            Token to be processed.
        pos_tag : str
            Part-of-Speech tag for `token`.

        Returns
        -------
            str: Lemmatized token.

        """
        from nltk.corpus import wordnet as wn

        tag = {
            'N': wn.NOUN,
            'V': wn.VERB,
            'R': wn.ADV,
            'J': wn.ADJ,
            'S': wn.ADJ_SAT
        }.get(pos_tag[0], wn.NOUN)
        return self.lemmatizer.lemmatize(token, tag)

    def clean_token(self, token):
        """
        Cleans `token` by performing the following steps:
            1. Converts to lower-case and strips whitespace.
            2. If `token` is a stopword and `remove_stopwords` is True,
               return an empty string.
            3. Removes non-alpha characters from word.

        Parameters
        ----------
        token : str
            String to be cleaned.

        Returns
        -------
            c_token (str): Cleaned string.
        """
        c_token = token.lower().strip()
        if self.remove_stopwords and c_token in self.stopwords:
            return ''
        # remove non-alpha characters
        c_token = filter(lambda x: x.isalpha(), c_token)
        return c_token

    def process(self, document):
        """
        Preprocessing method that stems and/or lemmatizes token
        during a single pass through data.
        """
        cleaned_tokens = []
        if self.do_lemmatize:
            from nltk import pos_tag as nltk_pos_tag

            # lemmatizing requires that each token has an associated POS tag
            postag_doc = nltk_pos_tag(document.split())
            for token, tag in postag_doc:
                token = self.clean_token(token)
                token = self.lemmatize(token, tag)
                if self.do_stem:
                    token = self.stem(token)
                cleaned_tokens.append(token)
        else:
            for token in document.split():
                token = self.clean_token(token)
                if self.do_stem:
                    token = self.stem(token)
                cleaned_tokens.append(token)

        keep_tokens = [ctoken for ctoken in cleaned_tokens if ctoken != '']
        # determine whether we should return list of tokens or single str
        if not self.return_list:
            return ' '.join(keep_tokens)
        return keep_tokens

    def fast_process(self, document):
        """
        Fast preprocessing of document without stemming or lemmatizing tokens.
        Suitable preprocessing for word2vec.

        Parameters
        ----------
        document: str
            Raw text of document.

        Returns
        -------
            iterable: List of reprocessed tokens from document.
        """
        doc = [
            self.clean_token(token)
            for token in document.split()
        ]
        clean_doc = [token for token in doc if token != '']
        if not self.return_list:
            return ' '.join(clean_doc)
        return clean_doc

    def fit(self, X, y=None):
        """
        `fit` method required for inclusion in sklearn pipeline object.
        Returns data as is.
        """
        return self

    def transform(self, documents):
        """
        Preprocesses each document in `documents`.

        Parameters
        ----------
        documents: iterable
            List of documents. Each document raw, untokenized text.

        Returns
        -------
            iterable: list of lists. Each list contains the preprocessed
            tokens for a document.
        """
        document_list = []
        for document in documents:
            document_list.append(self.preprocess(document))
        return document_list
