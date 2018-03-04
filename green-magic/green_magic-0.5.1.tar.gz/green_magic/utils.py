from gensim.utils import tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from . import definitions


class ClusterManager:

    def __init__(self, weedmaster):
        self._wm = weedmaster
        self.selected_id = None

    def __getitem__(self, _id):
        self.selected_id = _id
        return self

    def get_clusters(self, som, nb_clusters=8):
        self.selected_id = self._wm.map_manager.map_obj2id[som]
        return self._create_clusters(som, nb_clusters=nb_clusters)


def get_normalizer(norm_type):
    """
    Returns a lambda function that acts as a normalizer for input words/tokens.\n
    :param norm_type: the normalizer type to "construct". Recommended 'lemmatize'. If type is not in the allowed types then does not normalize (lambda just forwards the input to output as it is)
    :type norm_type: {'stem', 'lemmatize'}
    :return: the lambda callable object to perform normalization
    :rtype: lambda
    """
    if norm_type == 'stem':
        from nltk.stem import PorterStemmer
        stemmer = PorterStemmer()
        return lambda x: stemmer.stem(x)
    elif norm_type == 'lemmatize':
        from nltk.stem import WordNetLemmatizer
        lemmatizer = WordNetLemmatizer()
        return lambda x: lemmatizer.lemmatize(x)
    else:
        return lambda x: x


def generate_tokens(text, normalizer='', word_filter='stopwords'):
    for w in (_.lower() for _ in tokenize(text)):
        if len(w) < 2:
            continue
        if word_filter == 'stopwords':
            if w in definitions.stop_words:
                continue
        yield get_normalizer(normalizer)(w)


def generate_tokens_with_padding(text, normalizer='', word_filter='stopwords'):
    yield '#'
    for w in (_.lower() for _ in tokenize(text)):
        if word_filter == 'stopwords':
            if w in definitions.stop_words:
                continue
        yield get_normalizer(normalizer)(w)
    yield '#'


def gen_values(extr_output):
    if type(extr_output) == list:
        for i in extr_output:
            yield i
    elif type(extr_output) == str:
        yield extr_output
    else:  # dictionary like
        for k, v in extr_output.items():
            yield k, v


def extract_value(strain, field):
    if field in definitions.grow_info:
        return strain['grow_info'][field]
    else:
        return strain[field]


def empty_field(strain, field):
    return definitions.field2empty_obj[field] == extract_value(strain, field)


def generate_word(text_data, normalize='lemmatize', word_filter=True):
    """
    Given input text_data, a normalize 'command' and a stopwords filtering flag, generates a normalized, lowercased word/token provided that it passes the filter and that its length is bigger than 2 characters.\n
    :param text_data: the text from which to generate (i.e. doc['text'])
    :type text_data: str
    :param normalize: the type of normalization to perform. Recommended 'lemmatize'
    :type normalize: {'stem', 'lemmatize'}, else does not normalize
    :param word_filter: switch/flag to control stopwords filtering
    :type word_filter: boolean
    :return: the generated word/token
    :rtype: str
    """
    normalizer = get_normalizer(normalize)
    if word_filter:
        print("  stopwords are being filtered")
    for word in (_.lower() for _ in tokenize(text_data)):
        if len(word) < 2:
            continue
        if word_filter and word in stop_words:
            continue
        yield normalizer(word)
