# -*-coding:utf-8 -*
"""Definitions a the context of a word in a sentence

This module defines classes to be used as `context` parameter in the
:func:`mangoes.counting.count_cooccurrence` function.

Examples
--------

    >>> window_3 = mangoes.context.Window(window_half_size=3)
    >>> contexts = window_3(['The', 'quick', 'brown', 'fox', 'jumps', 'over', 'the', 'lazy', 'dog'])
    >>> contexts[0]
    ['quick', 'brown', 'fox']
    >>> contexts[4]
    ['quick', 'brown', 'fox', 'over', 'the', 'lazy']
    >>> contexts[5]
    ['brown', 'fox', 'jumps', 'the', 'lazy', 'dog']
    >>> contexts[7]
    ['jumps', 'over', 'the', 'dog']

"""
import abc
import logging
import random

import mangoes
import mangoes.utils.exceptions

_logger = logging.getLogger(__name__)


class Context:
    """Base callable class to define the context of a word in a sentence

    Parameters
    ----------
    vocabulary: mangoes.Vocabulary or list of string
        vocabulary of the words to consider in the context. Other words are ignored.

    See Also
    --------
    :func:`mangoes.counting.count_cooccurrence`
    """
    def __init__(self, vocabulary=None):
        self._params = {}
        self.vocabulary = vocabulary
        try:
            self.filter_sentence = mangoes.vocabulary.create_tokens_filter(vocabulary.entity)
        except AttributeError:
            # no vocabulary or vocabulary has no attribute entity
            def no_filter(sentence):
                return sentence
            self.filter_sentence = no_filter

    @abc.abstractmethod
    def __call__(self, sentence, mask=False):
        """Returns the elements in the defined context for each word in sentence

        This function extracts the list of elements found in the context of the elements of a sentence

        Parameters
        ----------
        sentence: list
            The sentence as a list of words or tokens
        mask: list of bool
            List of booleans that indicates the positions in the sentence that can be ignored (value=False) :
            empty contexts will be returned for these words

        Returns
        -------
        list of the same size than sentence
        """
        pass

    @property
    def params(self):
        """Parameters of the context"""
        return self._params


class Sentence(Context):
    """Implements sentence context

     This context extracts the list of tokens in a sentence, around each word, barring the
     word itself.

    """
    def __init__(self, vocabulary=None):
        super().__init__(vocabulary)

    def __call__(self, sentence, mask=False):
        filtered_sentence = self.filter_sentence(sentence)
        return [[w for w in filtered_sentence[0:position] + filtered_sentence[position + 1:len(filtered_sentence)]
                 if not self.vocabulary or w in self.vocabulary]
                if not mask or mask[position] else [] for position in range(len(filtered_sentence))]


class Window(Context):
    """Implements window-type context

    This context extracts the list of elements found in a window defined around each word, barring the
    word itself.

    Parameters
    ----------
    symmetric: boolean (def = True)
        if the window is symmetric (default), the window will be centered around the position, and window_half_size
        must be an integer.

    window_half_size: int if symmetric, tuple of 2 int if not
        size of the search space to the left and to the right of 'position' word (default = 1)

    dirty: boolean (def = False)
        if True and some of the words in the window aren't correct ids (ex : -1), they will not be fetched, but the
        window will be extended further so as to still be able to meet the quota of 2*'window_half_size' (if
        symmetric) words to fetch.

    dynamic: boolean
        if True, the size of the actual window is sampled between 1 and `window_half_size`

    """
    def __init__(self, vocabulary=None, symmetric=True, window_half_size=1, dirty=False, dynamic=False):
        super().__init__(vocabulary)

        self._params.update({"symmetric": symmetric, "window_half_size": window_half_size, "dirty": dirty,
                             "dynamic": dynamic})

        if symmetric:
            self.size_before = self.size_after = window_half_size
        else:
            self.size_before, self.size_after = window_half_size

        if dirty:
            if dynamic:
                self._window = _window_dirty_dynamic
            else:
                self._window = _window_dirty
        else:
            if dynamic:
                self._window = _window_clean_dynamic
            else:
                self._window = _window_clean

    def __call__(self, sentence, mask=False):
        filtered_sentence = self.filter_sentence(sentence)
        return [self._window(position, filtered_sentence, self.vocabulary, self.size_before, self.size_after)
                if not mask or mask[position] else [] for position in range(len(filtered_sentence)) ]


def _window_clean(position, sentence, vocabulary, size_before=0, size_after=1):
    before_list = [w for w in sentence[max(0, position - size_before):position]
                   if not vocabulary or w in vocabulary]
    after_list = [w for w in sentence[position + 1:min(position + size_after + 1, len(sentence))]
                  if not vocabulary or w in vocabulary]
    return before_list + after_list


def _window_clean_dynamic(position, sentence, vocabulary, max_size_before=0, max_size_after=1):
    size_before, size_after = _get_random_size(max_size_before, max_size_after)
    return _window_clean(position, sentence, vocabulary, size_before, size_after)


def _window_dirty(index, sentence, vocabulary, size_before=0, size_after=1):
    before_list = []
    after_list = []

    i = index - 1
    while i >= 0 and len(before_list) < size_before:
        if sentence[i] in vocabulary:
            before_list.append(sentence[i])
        i -= 1
    before_list = list(reversed(before_list))

    i = index + 1
    while i < len(sentence) and len(after_list) < size_after:
        if sentence[i] in vocabulary:
            after_list.append(sentence[i])
        i += 1

    return before_list + after_list


def _window_dirty_dynamic(index, sentence, vocabulary, max_size_before=0, max_size_after=1):
    size_before, size_after = _get_random_size(max_size_before, max_size_after)
    return _window_dirty(index, sentence, vocabulary, size_before, size_after)


def _get_random_size(max_size_before, max_size_after):
    size_before = random.randint(1, max_size_before) if max_size_before > 0 else 0
    if max_size_after == max_size_before:
        size_after = size_before
    else:
        size_after = random.randint(1, max_size_after) if max_size_after > 0 else 0
    return size_before, size_after


class DependencyBasedContext(Context):
    """Implements Dependency-Based context

    Returns the modifiers and the head of each element of a sentence.

    Examples
    --------
    >>> source = mangoes.corpus.CONLLU(["1	australian	australian	ADJ	JJ	_	2	amod	_	_",
    >>>                                 "2	scientist	scientist	NOUN	NN	_	3	nsubj	_	_",
    >>>                                 "3	discovers	discover	VERB	VBZ	_	0	root	_	_",
    >>>                                 "4	star	star	NOUN	NN	_	3	dobj	_	_",
    >>>                                 "5	with	with	ADP	IN	_	6	case	_	_",
    >>>                                 "6	telescope	telescope	NOUN	NN	_	3	nmod	_	_"])
    >>> sentence = source.sentences().__next__()
    >>> context = mangoes.context.DependencyBasedContext(labels=True)
    >>> context(sentence)[1] # scientist
    {"australian/amod", "discovers/nsubj-"}

    References
    ----------
    .. [1] Levy, O., & Goldberg, Y. (2014, June). Dependency-Based Word Embeddings. In ACL (2) (pp. 302-308).

    Parameters
    ----------
    dependencies: {'universal-dependencies', 'stanford-dependencies'} or callable
        Representation used for dependencies annotation. Default is 'universal-dependencies'.
        You can also provide your own parser

    collapse: bool
        Whether or not the preposition relations should be collapsed. Default is False.

    labels: bool
        Whether or not the labels should be added to the output contexts. Default is False

    """
    def __init__(self, vocabulary=None, entity="form", dependencies="universal-dependencies",
                 collapse=False, labels=False, depth=1):
        super().__init__(vocabulary)

        if labels:
            self.filter_vocabulary = self.vocabulary
            self.vocabulary = mangoes.vocabulary.DynamicVocabulary()
            self._format_context = self._format_context_with_label
        else:
            self.filter_vocabulary = self.vocabulary
            self._format_context = self._format_context_without_label

        self.entity = entity
        self.filter_token = mangoes.vocabulary.create_token_filter(entity)

        self._params.update({"parser": dependencies, "collapse": collapse, "labels": labels, "depth": depth})
        if dependencies == "universal-dependencies":
            self.sentence_parser = self.ud_sentence_parser
        elif dependencies == "stanford-dependencies":
            self.sentence_parser = self.stanford_dependencies_sentence_parser
        elif callable(dependencies):
            self.sentence_parser = dependencies
        else:
            raise mangoes.utils.exceptions.NotAllowedValue(dependencies, ["universal-dependencies", "stanford-dependencies"])

    @property
    def collapse(self):
        return self._params["collapse"]

    @property
    def labels(self):
        return self._params["labels"]

    @property
    def depth(self):
        return self._params["depth"]

    def __call__(self, sentence, mask=False):
        dependency_tree = self.sentence_parser(sentence, self.collapse)

        for _ in range(self.depth - 1):
            dependency_tree = self.add_children(dependency_tree)

        contexts = [set() for _ in sentence]
        for i, token_dependencies in enumerate(dependency_tree):
            if token_dependencies:
                head = self.filter_token(sentence[i])
                for target_id, label in token_dependencies:
                    target = self.filter_token(sentence[target_id])
                    if not self.filter_vocabulary or target in self.filter_vocabulary:
                        contexts[i].add(self._format_context(target, label, False))
                    if not self.filter_vocabulary or head in self.filter_vocabulary:
                        contexts[target_id].add(self._format_context(head, label, True))

        return contexts

    def _format_context_with_label(self, token, label, inverse):
        return token + "/" + label + "-"*inverse

    def _format_context_without_label(self, token, label, inverse):
        return token

    @staticmethod
    def add_children(sentence_tree):
        new_sentence_tree = []
        for token_children in sentence_tree:
            new_children = set(token_children)
            for child, child_label in token_children:
                if sentence_tree[child]:
                    for grand_child, grand_child_label in sentence_tree[child]:
                        new_children.add((grand_child, child_label + '_' + grand_child_label))
            new_sentence_tree.append(new_children)
        return new_sentence_tree

    @staticmethod
    def ud_sentence_parser(sentence, collapse=False):
        """Returns an adjacency list from a sentence annotated with Universal Dependencies

        Examples
        --------
        >>> source = mangoes.corpus.CONLLU(["1	australian	australian	ADJ	JJ	_	2	amod	_	_",
        >>>                                 "2	scientist	scientist	NOUN	NN	_	3	nsubj	_	_",
        >>>                                 "3	discovers	discover	VERB	VBZ	_	0	root	_	_",
        >>>                                 "4	star	star	NOUN	NN	_	3	dobj	_	_",
        >>>                                 "5	with	with	ADP	IN	_	6	case	_	_",
        >>>                                 "6	telescope	telescope	NOUN	NN	_	3	nmod	_	_"])
        >>> sentence = source.sentences().__next__()
        >>> mangoes.context.DependencyBasedContext.ud_sentence_parser(sentence)
        [set(),
         {(0, 'amod')},
         {(1, 'nsubj'), (3, 'dobj'), (5, 'nmod')},
         set(),
         set(),
         {(4, 'case')}]

        Parameters
        ----------
        sentence: list of Tokens

        collapse: boolean
            Whether or not to collapse prepositions

        Returns
        -------
        list of same size as sentence
            Returns the dependents of each token in the sentence.

        """
        root_label = "root"
        preposition_label = "case"
        preposition_object_label = "nmod"

        relations = [set() for _ in sentence]

        for token in sentence:
            try:
                if token.dependency_relation == root_label:
                    continue
                elif collapse and token.dependency_relation == preposition_label:
                    preposition_object_position = int(token.head) - 1
                    preposition_object = sentence[preposition_object_position]

                    head_position = int(preposition_object.head) - 1

                    relations[head_position].add(
                        (preposition_object_position, preposition_label + "_" + token.form))
                elif collapse and token.dependency_relation == preposition_object_label:
                    continue  # done in the previous case
                else:
                    token_position = int(token.id) - 1
                    head_position = int(token.head) - 1

                    relations[head_position].add((token_position, token.dependency_relation))
            except ValueError:
                logging.warning("Unable to parse token %s in sentence %s (ValueError)",
                                token, " ".join([t.form for t in sentence]))
                continue
            except IndexError:
                logging.warning("Unable to parse token %s in sentence %s (IndexError)",
                                token, " ".join([t.form for t in sentence]))
                continue

        return relations

    @staticmethod
    def stanford_dependencies_sentence_parser(sentence, collapse=False):
        """Returns an adjacency list from a sentence annotated with Stanford Dependencies

        See Also
        --------
        DependencyBasedContext.universal_dependencies_parse_sentence()

        Parameters
        ----------
        sentence: list of Tokens

        collapse: boolean
            Whether or not to collapse prepositions

        Returns
        -------
        list of same size as sentence
            Returns the dependents of each token in the sentence.

        """
        root_label = "root"
        preposition_label = "prep"
        preposition_object_label = "pobj"

        relations = [set() for _ in sentence]

        for token in sentence:
            if token.dependency_relation == root_label:
                continue
            elif collapse and token.dependency_relation == preposition_label:
                continue
            elif collapse and token.dependency_relation == preposition_object_label:
                preposition = sentence[(int(token.head) - 1)]
                token_position = int(token.id) - 1
                head_position = int(preposition.head) - 1

                relations[head_position].add((token_position, preposition_label + "_" + preposition.form))
            else:
                token_position = int(token.id) - 1
                head_position = int(token.head) - 1

                relations[head_position].add((token_position, token.dependency_relation))

        return relations
