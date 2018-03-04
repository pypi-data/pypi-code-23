import nltk
import string
from nltk.corpus import stopwords

sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

def to_sentences(document):
    '''
    Take a string as input and splits the string into sentences
    :param document:
    :return a list of strings, where each item is a sentence of the document:
    '''
    split_sentences = sentence_tokenizer.tokenize(document)

    return split_sentences

def tokenize(text):
    '''
    return the piece of text as a list of strings, where each string is a word
    :param text:
    :return:
    '''
    return nltk.word_tokenize(text)

def untokenize(tokens):
    '''
    Turn a list of tokens into a fully formed sentence
    Attempts to preserve things like "can't"
    :param tokens:
    :return:
    '''
    return "".join([" " + i if not i.startswith("'")
                               and i not in string.punctuation
                            else i
                    for i in tokens]).strip()

def remove_stops(tokens):
    '''
    Stops words are common word without much semantic value
    e.g. "of", "and", "while", etc.
    :param tokens:
    :return:
    '''
    stop_words = list(stopwords.words('english'))
    return [t for t in tokens if t not in stop_words]

def words_only(total_tokens):
    '''
    Filter the tokens to remove tokens which are not English words
    :param total_tokens:
    :return:
    '''
    raise NotImplementedError