# -*- coding: utf-8 -*-
"""Classes and functions to evaluate embeddings.

"""

import abc
import heapq
import logging
from collections import namedtuple

import numpy as np
import scipy.stats

import mangoes.dataset
import mangoes.utils.arrays
import mangoes.utils.metrics

NA = "Not Applicable"  # TODO : temporary, find a better way to handle missing values


class _Result:
    """Abstract base class to store the result of evaluation tasks

    Warnings
    --------

    This class should not be used directly.
    Use derived classes instead.

    """
    LINE_LENGTH = 96
    COL = 4

    def __init__(self, dataset, predictions, oov=NA, ignored=NA):
        self._logger = logging.getLogger("{}.{}".format(__name__, self.__class__.__name__))

        self.dataset = dataset
        self.predictions = predictions

        self.score = self.get_score()
        self.oov = oov
        self.ignored = ignored

        self._results_dict = self._detail(self.dataset.subsets_to_questions)

    @property
    def summary(self):
        """Returns a printable string with a summary of the results of the evaluation

        Display the global score, the number of evaluated questions and the total number of questions in the dataset.

        See Also
        --------
        detail
        more_detail
        """
        return self.to_string(show_subsets=False)

    @property
    def detail(self):
        """Returns a printable string with the results of the evaluation for each subset of the dataset

        Display the score, the number of evaluated questions and the total number of questions in the subset
        for each subset of the dataset.

        See Also
        --------
        summary
        more_detail
        """
        return self.to_string(show_subsets=True, show_NA=False)

    @property
    def more_detail(self):
        """Returns a printable string with the detail of the results of the evaluation for each subset

        Display the score, the number of evaluated questions and the total number of questions and the prediction
        for each question and each subset of the dataset.

        See Also
        --------
        summary
        detail
        """
        return self.to_string(show_subsets=True, show_questions=True)

    def get_score(self, subset=None):
        """Returns the score of a subset of the dataset"""
        # TODO: implements macro/micro-average
        return self._compute_score([(g, self.predictions[q])
                                    for q, g in self.dataset.get_questions_and_gold(subset)
                                    if q in self.predictions])

    def _detail(self, data, name=""):
        result = {}

        for subset_name, subset_data in data.items():
            fullname = name + "/" + subset_name
            result[subset_name] = {}
            result[subset_name]["score"] = self.get_score(fullname)
            result[subset_name]["nb_questions_in_subset"] = mangoes.dataset.nb_questions(subset_data)
            if isinstance(subset_data, dict):
                result[subset_name]["subsets"] = self._detail(subset_data, name=fullname)
            else:
                questions = {}
                for question_w_gold in subset_data:
                    question = self.dataset.parse_question(question_w_gold).question
                    if question in self.predictions:
                        questions[question_w_gold] = self.predictions[question]
                if questions:
                    result[subset_name]["questions"] = questions
        return result

    def to_string(self, show_subsets=True, show_questions=False, show_NA=True):
        """Returns a printable version of the results

        Parameters
        ----------
        show_subsets: boolean
            if True, include the results of each subset of the dataset. If False, only the global score
        show_questions: boolean
            if True, show the predictions for each evaluated question
        show_NA: boolean
            if False, hide the subsets for which no question has been evaluated

        Returns
        -------
        str

        """
        string = ""
        for subset in self._results_dict.items():
            string += self._subset_to_string(subset, show_subsets=show_subsets, show_questions=show_questions,
                                             show_NA=show_NA, header=True)
        return string

    def _subset_to_string(self, subset, show_subsets=True, show_questions=False, show_NA=True,
                          header=False, dec=0):
        tab = " " * self.COL

        string = ""
        name, detail = subset

        if detail["score"]:
            if header:
                string += self._detail_header(dec, tab)
            else:
                string += "-" * self.LINE_LENGTH + "\n"
            string += self._detail_summary(name, detail, dec, tab)
        elif show_NA:
            string += self._detail_na(name, detail, dec, tab)

        if show_subsets and "subsets" in detail:
            for subset in detail["subsets"].items():
                string += self._subset_to_string(subset, dec=dec + 1, show_questions=show_questions, show_NA=show_NA)
        elif show_questions and "questions" in detail:
            string += "\n"
            string += self._detail_questions_header(dec, tab)
            for question, prediction in detail["questions"].items():
                string += self._detail_question(self.dataset.parse_question(question), prediction, dec, tab)
        return string

    @classmethod
    def _detail_na(cls, name, detail, dec, tab):
        line = "-" * cls.LINE_LENGTH + "\n"
        line += "{:<{width}}".format(tab * dec + name, width=(cls.LINE_LENGTH - 9 * cls.COL))
        line += "{:>{width}}".format("0/{}".format(detail["nb_questions_in_subset"]), width=3 * cls.COL)
        line += "{:>{width}}".format("Not available", width=6 * cls.COL)
        return line + "\n"

    @classmethod
    def _nb_questions(cls, subset):
        if isinstance(subset, list):
            return len(subset)
        if "questions" in subset:
            return len(subset["questions"])
        if "subsets" in subset:
            return sum([cls._nb_questions(subset["subsets"][s]) for s in subset["subsets"]])
        return 0

    @abc.abstractclassmethod
    def _compute_score(cls, data):
        pass

    @abc.abstractclassmethod
    def _detail_question(cls, question, prediction, dec, tab):
        pass

    @abc.abstractclassmethod
    def _detail_questions_header(cls, dec, tab):
        pass

    @abc.abstractclassmethod
    def _detail_summary(cls, name, score, dec, tab):
        pass

    @abc.abstractclassmethod
    def _detail_header(cls, dec, tab):
        pass


# ################ Analogy
class AnalogyResult(_Result):
    """Class to handle the result of analogies evaluation

    Attributes
    ----------
    dataset: mangoes.dataset.Dataset
        the dataset used to evaluate

    predictions: dict
        A dictionary where keys are the questions of the dataset (without gold) and the values are a tuple with
        the answers predicted with an Embedding using 3COSMUL and 3COSADD respectively

    score: AnalogyResult.Score
        Global score. The score is a tuple with the percentage of questions where the expected answer is in
        the predictions computed using, respectively, 3COSADD and 3COSMUL

    oov: set of strings
        words of the dataset that are not represented in the embedding

    ignored: int
        number of questions of the dataset ignored in the evaluation

    summmary
    detail
    more_detail

    """
    Score = namedtuple("Score", ["cosadd", "cosmul"])

    @classmethod
    def _compute_score(cls, data):
        if data:
            score_add, score_mul = 0, 0
            for gold, prediction in data:
                if gold in prediction[0]:
                    score_add += 1
                if gold in prediction[1]:
                    score_mul += 1
            return cls.Score(score_add / len(data), score_mul / len(data))

    @classmethod
    def _detail_header(cls, dec, tab):
        line = "{:>{width}}".format("", width=cls.LINE_LENGTH - 9 * cls.COL)
        line += "{:>{width}}".format("Nb questions", width=3 * cls.COL)
        line += "{:>{width}}".format("cosadd", width=3 * cls.COL)
        line += "{:>{width}}".format("cosmul", width=3 * cls.COL)
        return line + "\n" + "=" * cls.LINE_LENGTH + "\n"

    @classmethod
    def _detail_summary(cls, name, detail, dec, tab):
        score = detail["score"]
        nb_questions_in_subset = detail["nb_questions_in_subset"]
        nb_questions = cls._nb_questions(detail)

        line = "{:<{width}}".format(tab * dec + name, width=(cls.LINE_LENGTH - 3 * 3 * cls.COL))
        line += "{:>{width}}".format("{}/{}".format(nb_questions, nb_questions_in_subset), width=3 * cls.COL)
        line += "{:>{width}}".format("{:.2%}".format(score.cosadd), width=3 * cls.COL)
        line += "{:>{width}}".format("{:.2%}".format(score.cosmul), width=3 * cls.COL)

        return line + "\n"

    @classmethod
    def _detail_question(cls, question, prediction, dec, tab):
        question = " ".join(question)
        cosadd, cosmul = prediction

        line = "{:{width}}".format(tab * dec + question, width=(cls.LINE_LENGTH - 6 * cls.COL))
        line += "{:>{width}}".format(", ".join(cosadd), width=3 * cls.COL)
        line += "{:>{width}}".format(", ".join(cosmul), width=3 * cls.COL)
        return line + "\n"

    @classmethod
    def _detail_questions_header(cls, dec, tab):
        return ""


def analogy(embedding, dataset="all", allowed_answers=1, epsilon=0.001):
    """Evaluate an embedding on analogy task

    Parameters
    ----------
    embedding: mangoes.Embeddings
        The representation to evaluate
    dataset: mangoes.Dataset
        The dataset to use
    allowed_answers
        Number of answers
    epsilon: float
        Value used to prevent division by zero in 3CosMul

    Returns
    -------
    AnalogyResult

    """
    if not embedding or not dataset:
        return NA

    if dataset == "all":
        dataset = mangoes.dataset.load("analogy", language=embedding.words.language)

    selected_questions, common_words, oov, nb_ignored_questions = _filter_analogies(dataset, embedding)

    normalized_embedding = embedding.matrix.normalize()

    dataset_vocabulary = mangoes.Vocabulary(list(common_words))
    dataset_matrix = normalized_embedding[[embedding.words.index(word) for word in dataset_vocabulary]]

    if normalized_embedding.all_positive():
        similarities = mangoes.utils.metrics.pairwise_cosine_similarity(dataset_matrix,
                                                                        normalized_embedding,
                                                                        normalize=False)
    else:
        similarities = mangoes.utils.metrics.pairwise_non_negative_cosine_similarity(dataset_matrix,
                                                                                     normalized_embedding,
                                                                                     normalize=False)

    predictions = _evaluate_analogies(selected_questions, dataset_vocabulary, embedding.words, similarities,
                                      allowed_answers, epsilon)

    return AnalogyResult(dataset,
                         {question: prediction for question, prediction in zip(selected_questions, predictions)},
                         oov=oov, ignored=nb_ignored_questions)


def _filter_analogies(dataset, embedding):
    """From a dataset, keep only the questions where all words are in the dataset

    Parameters
    ----------
    dataset: mangoes.dataset.Dataset
    embedding: mangoes.Embeddings

    Returns
    -------
    questions : list of questions (question = list of string, without gold)
        list of the questions of the dataset where all words are in the dataset
    words : set of strings
        set of all the words of the questions
    oov_words: set of strings
        set of all the words from the dataset that are not represented in the embedding
    nb_ignored: int
        number of ignored questions
    """
    questions, words, oov_words = set(), set(), set()
    nb_ignored = 0

    for question_w_gold in dataset.questions_to_subsets:
        oov_words_in_question = [w for w in question_w_gold.split() if w not in embedding.words]
        if not oov_words_in_question:
            question, _ = question_w_gold.rsplit(maxsplit=1)
            questions.add(question)
            words.update(question.split())
        else:
            oov_words.update(oov_words_in_question)
            nb_ignored += 1

    return list(questions), words, oov_words, nb_ignored


def _evaluate_analogies(list_of_questions, dataset_vocabulary, candidate_vocabulary, similarities,
                        allowed_answers, epsilon):
    return [_resolve_analogy(question, dataset_vocabulary, candidate_vocabulary, similarities, allowed_answers, epsilon)
            for question in list_of_questions]


def _resolve_analogy(question, dataset_vocabulary, candidate_vocabulary, similarities,
                     allowed_answers, epsilon):
    a, b, c = question.split()

    a_similarities = similarities[dataset_vocabulary.index(a)]
    b_similarities = similarities[dataset_vocabulary.index(b)]
    c_similarities = similarities[dataset_vocabulary.index(c)]

    question_terms_indices = [candidate_vocabulary.index(word) for word in (a, b, c)]

    scores_add = b_similarities - a_similarities + c_similarities
    scores_add[question_terms_indices] = np.NINF
    best_answer_add = [candidate_vocabulary[i] for i in _get_n_best(allowed_answers, scores_add)]

    scores_mul = b_similarities * c_similarities / (a_similarities + epsilon)
    scores_mul[question_terms_indices] = np.NINF
    best_answer_mul = [candidate_vocabulary[i] for i in _get_n_best(allowed_answers, scores_mul)]

    return best_answer_add, best_answer_mul


def _get_n_best(nb_best, scores):
    if nb_best == 1:
        return [np.nanargmax(scores)]

    return heapq.nlargest(nb_best, range(len(scores)), key=lambda i: scores[i])


# ############## Similarity

class SimilarityResult(_Result):
    """Class to handle the result of word similarity evaluation

    Attributes
    ----------
    dataset: mangoes.dataset.Dataset
        the dataset used to evaluate

    predictions: dict
        A dictionary where keys are the questions of the dataset (without gold) and the values are the computed
        similarity

    score: SimilarityResult.Score
        Global score. The score is a tuple of the 2 correlation coefficient : Pearson and Spearman, respectively.
        Each coefficient is a tuple with the coefficient itself and the p-value.

    oov: set of strings
        words of the dataset that are not represented in the embedding

    ignored: int
        number of questions of the dataset ignored in the evaluation

    summmary
    detail
    more_detail

    """
    Coeff = namedtuple("Coeff", ["coeff", "pvalue"])
    Score = namedtuple("Score", ["pearson", "spearman"])

    @classmethod
    def _compute_score(cls, data):
        if data:
            gold = [float(d[0]) for d in data]
            predictions = [d[1] for d in data]

            pearson = cls.Coeff(*scipy.stats.pearsonr(predictions, gold))
            spearman = cls.Coeff(*scipy.stats.spearmanr(predictions, gold))

            return cls.Score(pearson, spearman)

    @classmethod
    def _detail_header(cls, dec, tab):
        line = "{:>{width}}".format("", width=cls.LINE_LENGTH - 8 * cls.COL)
        line += "{:>{width}}".format("pearson", width=4 * cls.COL)
        line += "{:>{width}}".format("spearman", width=4 * cls.COL)
        line += "\n"
        line += "{:>{width}}".format("", width=cls.LINE_LENGTH - 11 * cls.COL)
        line += "{:>{width}}".format("Nb questions", width=3 * cls.COL)
        line += "{:>{width}}".format("(p-value)", width=4 * cls.COL)
        line += "{:>{width}}".format("(p-value)", width=4 * cls.COL)
        return line + "\n" + "=" * cls.LINE_LENGTH + "\n"

    @classmethod
    def _detail_summary(cls, name, detail, dec, tab):
        score = detail["score"]
        nb_questions_in_subset = detail["nb_questions_in_subset"]
        nb_questions = cls._nb_questions(detail)

        line = "{:<{width}}".format(tab * dec + name, width=(cls.LINE_LENGTH - 11 * cls.COL))
        line += "{:>{width}}".format("{}/{}".format(nb_questions, nb_questions_in_subset), width=3 * cls.COL)
        line += "{:>{width}}".format("{:.2}({:.2e})".format(*score.pearson), width=4 * cls.COL)
        line += "{:>{width}}".format("{:.2}({:.2e})".format(*score.spearman), width=4 * cls.COL)
        return line + "\n"

    @classmethod
    def _detail_questions_header(cls, dec, tab):
        width = (cls.LINE_LENGTH - dec * cls.COL) // 4

        line = tab * dec
        line += "{:{width}}".format("", width=width)
        line += "{:{width}}".format("", width=width)
        line += "{:{width}}".format("gold", width=width)
        line += "{:{width}}".format("score", width=width)
        return line + "\n"

    @classmethod
    def _detail_question(cls, question, prediction, dec, tab):
        width = (cls.LINE_LENGTH - dec * cls.COL) // 4
        question, gold = question
        word1, word2 = question.split()

        line = tab * dec
        line += "{:{width}}".format(word1, width=width)
        line += "{:{width}}".format(word2, width=width)
        line += "{:{width}}".format(gold, width=width)
        line += "{:{width}}".format("{:.2f}".format(prediction), width=width)
        return line + "\n"


def similarity(embedding, dataset="all", metric=mangoes.utils.metrics.rowwise_cosine_similarity):
    """Evaluate an embedding on word similarity task

    Parameters
    ----------
    embedding: mangoes.Embeddings
        The representation to evaluate
    dataset: mangoes.Dataset
        The dataset to use
    metric
        the metric to use to compute the similarity (default : cosine)

    Returns
    -------
    SimilarityResult

    """
    if not embedding or not dataset:
        return NA

    if dataset == "all":
        dataset = mangoes.dataset.load("similarity", language=embedding.words.language)

    selected_questions, _, oov, nb_ignored_questions = _filter_similarities(dataset, embedding)

    predictions = _evaluate_similarities(selected_questions, embedding, metric)

    return SimilarityResult(dataset,
                            {question: prediction for question, prediction in zip(selected_questions, predictions)},
                            oov=oov, ignored=nb_ignored_questions)


def _evaluate_similarities(words_pairs, embedding, metric):
    words_pairs_indices = np.array([[embedding.words.index(q.split()[0]),
                                     embedding.words.index(q.split()[1])]
                                    for q in words_pairs])

    first_terms = embedding.matrix[words_pairs_indices[:, 0], :]
    second_terms = embedding.matrix[words_pairs_indices[:, 1], :]

    predictions = metric(first_terms, second_terms)

    return predictions


def _filter_similarities(dataset, embedding):
    """From a dataset, keep only the questions where all words are in the dataset

    Parameters
    ----------
    dataset: mangoes.dataset.Dataset
    embedding: mangoes.Embeddings

    Returns
    -------
    questions : list of questions (question = list of string, without gold)
        list of the questions of the dataset where all words are in the dataset
    words : set of strings
        set of all the words of the questions
    oov_words: set of strings
        set of all the words from the dataset that are not represented in the embedding
    nb_ignored: int
        number of ignored questions
    """
    questions, words, oov_words = set(), set(), set()
    nb_ignored = 0

    for question_w_gold in dataset.questions_to_subsets:
        oov_words_in_question = [w for w in dataset.parse_question(question_w_gold).question.split()
                                 if w not in embedding.words]
        if not oov_words_in_question:
            question = dataset.parse_question(question_w_gold).question
            questions.add(question)
            words.update(question.split())
        else:
            oov_words.update(oov_words_in_question)
            nb_ignored += 1

    return list(questions), words, oov_words, nb_ignored


# ############## Outlier Detection

class OutlierDetectionResult(_Result):
    """Class to handle the result of outlier detection evaluation

    Attributes
    ----------
    dataset: mangoes.dataset.Dataset
        the dataset used to evaluate

    predictions: dict
        A dictionary where keys are the questions of the dataset and the values are the words of the question, sorted
        according to their compactness score

    score: OutlierDetectionResult.Score
        Global score. The score is a tuple with the Outlier Position Percentage and the Accuracy measures.

    oov: set of strings
        words of the dataset that are not represented in the embedding

    ignored: int
        number of questions of the dataset ignored in the evaluation

    summmary
    detail
    more_detail

    """
    Score = namedtuple("Score", ["opp", "accuracy"])

    def _detail(self, data, name=""):
        result = {}

        for subset_name, subset_data in data.items():
            fullname = name + "/" + subset_name

            result[subset_name] = {}
            result[subset_name]["score"] = self.get_score(fullname)
            result[subset_name]["nb_questions_in_subset"] = mangoes.dataset.nb_questions(subset_data)

            if isinstance(subset_data, dict):
                result[subset_name]["subsets"] = self._detail(subset_data, name=fullname)
            else:
                questions = {}
                for question_w_gold in subset_data:
                    if question_w_gold in self.predictions:
                        questions[question_w_gold] = self.predictions[question_w_gold]
                if questions:
                    result[subset_name]["questions"] = questions
        return result

    @classmethod
    def _detail_header(cls, dec, tab):
        line = "{:>{width}}".format("", width=cls.LINE_LENGTH - 9 * cls.COL)
        line += "{:>{width}}".format("Nb questions", width=3 * cls.COL)
        line += "{:>{width}}".format("OPP", width=3 * cls.COL)
        line += "{:>{width}}".format("accuracy", width=3 * cls.COL)
        return line + "\n" + "=" * cls.LINE_LENGTH + "\n"

    @classmethod
    def _detail_summary(cls, name, detail, dec, tab):
        score = detail["score"]
        nb_questions_in_subset = detail["nb_questions_in_subset"]
        nb_questions = cls._nb_questions(detail)

        line = "{:<{width}}".format(tab * dec + name, width=(cls.LINE_LENGTH - 9 * cls.COL))
        line += "{:>{width}}".format("{}/{}".format(nb_questions, nb_questions_in_subset), width=3 * cls.COL)
        line += "{:>{width}}".format("{:.2%}".format(score.opp), width=3 * cls.COL)
        line += "{:>{width}}".format("{:.2%}".format(score.accuracy), width=3 * cls.COL)
        return line + "\n"

    @classmethod
    def _detail_questions_header(cls, dec, tab):
        line = "{:>{width}}".format("outlier position", width=cls.LINE_LENGTH)
        return line + "\n"

    @classmethod
    def _detail_question(cls, question, prediction, dec, tab):
        line = "{:{width}}".format(tab * dec + question.question, width=(cls.LINE_LENGTH - 2 * cls.COL))
        line += "{:>{width}}".format(prediction.index(question.gold), width=2 * cls.COL)
        return line + "\n"

    @classmethod
    def _compute_score(cls, data):
        if data:
            gold = [d[0] for d in data]
            predictions = [d[1] for d in data]

            outlier_positions = [p.index(g) + 1 for p, g in zip(predictions, gold)]
            outlier_detections = [op == len(p) for p, op in zip(predictions, outlier_positions)]

            opp_score = sum([op / len(p) for p, op in zip(predictions, outlier_positions)]) / len(predictions)
            accuracy = sum(outlier_detections) / len(predictions)

            return cls.Score(opp_score, accuracy)


def outlier_detection(embedding, dataset="all"):
    """Evaluate an embedding on outlier detection task

     Parameters
     ----------
     embedding: mangoes.Embeddings
         The representation to evaluate
     dataset: mangoes.Dataset
         The dataset to use

     Returns
     -------
     SimilarityResult

     """
    if not embedding or not dataset:
        return NA

    if dataset == "all":
        dataset = mangoes.dataset.load("outlier_detection", language=embedding.words.language)

    selected_questions, _, oov, nb_ignored_questions = _filter_clusters(dataset, embedding)

    predictions = _evaluate_outliers(selected_questions, embedding)

    return OutlierDetectionResult(dataset,
                                  {question: prediction for question, prediction in
                                   zip(selected_questions, predictions)},
                                  oov=oov, ignored=nb_ignored_questions)


def _filter_clusters(dataset, embedding):
    questions, words, oov_words = set(), set(), set()
    nb_ignored = 0

    for question_w_gold, subset_path in dataset.questions_to_subsets.items():
        oov_words_in_question = [w for w in question_w_gold.split() if w not in embedding.words]
        if not oov_words_in_question:
            questions.add(question_w_gold)
            words.update(question_w_gold.split())
        else:
            oov_words.update(oov_words_in_question)
            nb_ignored += 1

    return list(questions), words, oov_words, nb_ignored


def _evaluate_outliers(selected_clusters, embedding):
    result = []
    for cluster in selected_clusters:
        compactness_scores = []
        for w in cluster.split():
            all_except_w = mangoes.utils.arrays.Matrix.factory(embedding.matrix[[embedding.words.index(word)
                                                                                 for word in cluster.split()
                                                                                 if word is not w]])
            compactness_scores.append(_pseudo_inversed_compactness_score(all_except_w, embedding[w]))

        sorted_indices = reversed(np.asarray(compactness_scores, dtype=float).argsort())
        result.append([cluster.split()[i] for i in sorted_indices])
    return result


def _pseudo_inversed_compactness_score(vectors, w):
    similarities = mangoes.utils.metrics.pairwise_cosine_similarity(w, vectors)
    return similarities.sum()


# ########################################
# Partition function
def _default_partition_function(embeddings, vector):
    """Default partition function

    Partition function used as default in function concentration_of_partition_function

    .. math::
        Z_c = \sum{\exp{c.w}}

    """
    return np.sum(np.exp(embeddings.matrix.dot(vector)))


def _generate_random_vectors(nb_vectors, dimension, mu):
    """Generate a list of uniformly random vectors
    """
    random_discourse_vectors = np.zeros(shape=(nb_vectors, dimension))
    for i in range(dimension):
        random_discourse_vectors[:, i] = np.random.normal(size=nb_vectors)
    return [(c / np.linalg.norm(c)) * (np.sqrt(dimension) / 5 / mu) for c in random_discourse_vectors]


def isotropy_from_partition_function(embeddings, discourse_vectors=1000,
                                     partition_function=_default_partition_function, epsilon=0.1):
    """Evaluate the isotropy of the representation computing the values of a partition function

    Compute the values of the repartition function (:math:`Z_c = \sum{\exp{cw}}`) for each :math:`c` in a set of
    uniformly random chosen vectors

    References
    ----------
    .. [1] Arora, S., Li, Y., Liang, Y., Ma, T., & Risteski, A. (2015). Rand-walk: A latent variable model approach to
           word embeddings.

    Parameters
    ----------
    embeddings: instance of Embeddings
        The :class:`mangoes.Embeddings` instance to evaluate
    discourse_vectors: int or list, optional
        a list of vectors or the number of vectors to pick uniformly on the sphere of norm 4/µ where µ is the average
        norm of the word vectors. Default : 1000.
    partition_function: callable
        the partition function to evaluate. Default : :func:`._default_partition_function`
    epsilon: float, optional
        determines the interval used to evaluate the concentration : [(1-ε)*mean_value, (1+ε)*mean_value]
        default: 0.1

    Returns
    -------
    tuple
        (concentration i.e. proportion of the values around the mean value, mean_value, values)

    """
    # TODO : only for dense matrices
    try:
        nb_random_vectors = len(discourse_vectors)
    except TypeError:
        nb_random_vectors = discourse_vectors
        discourse_vectors = _generate_random_vectors(nb_random_vectors,
                                                     embeddings.shape[1],
                                                     np.mean(np.linalg.norm(embeddings.matrix, axis=1)))

    partition_values = [partition_function(embeddings, c) for c in discourse_vectors]
    mean_value = np.mean(partition_values)
    nb_around_mean = (((1 - epsilon) * mean_value < partition_values)
                      & (partition_values < (1 + epsilon) * mean_value)).sum()
    return nb_around_mean / nb_random_vectors, mean_value, partition_values


# ########################################
# Distances between words

def _angles(vector, matrix, normalize=True):
    """Compute the angles between a vector and each line of the matrix

    Parameters
    ----------
    vector:
        a vector of dimension d
    matrix:
        a matrix n x d
    normalize: boolean, optional
        set to False if the matrix and the vectors are already normalized (default: True)

    Returns
    -------
    list
        list of angles size n
    """
    if normalize:
        matrix = matrix.normalize()
        vector = vector.normalize()

    cosines = matrix.dot(vector.T)
    try:
        cosines = cosines.todense()
    except AttributeError:
        pass

    # fix rounding errors
    cosines[[cosines > 1]] = 1
    cosines[[cosines < -1]] = -1

    return np.arccos(cosines)


def distances_one_word_histogram(embeddings, word, bins, distance=_angles, normalize=True):
    """Compute the values of an histogram of the distances between a word and all the other words of the Embeddings

    Parameters
    ----------

    embeddings: instance of Embeddings
        The :class:`mangoes.Embeddings` instance to evaluate
    word: str
        a word from the vocabulary of the Embedding
    bins: list
        bin edges, including the rightmost edge.
    distance: callable, optional
        the function to use to compute distances between words. Default: :func:`._angles`
    normalize: boolean, optional
        set to False if the matrix and the vectors are already normalized (default: True)

    Returns
    -------
    array
        an array of size (len(bins) - 1) with the values of the histogram
    """
    word_index = embeddings.words.word_index[word]
    matrix = mangoes.utils.arrays.Matrix.factory(
        np.concatenate((embeddings.matrix[:word_index], embeddings.matrix[word_index + 1:])))
    return np.histogram(distance(embeddings.matrix[word_index], matrix, normalize=normalize), bins=bins)[0]


def distances_histogram(embeddings, bins, distance=_angles, normalize=True):
    """Compute the values of an histogram of the distances between all the words of the Embeddings.

    Parameters
    ----------
    embeddings: instance of Embeddings
        The :class:`mangoes.Embeddings` instance to evaluate
    bins: list
        bin edges, including the rightmost edge.
    distance: callable
        the function to use to compute distances between words
    normalize: boolean
        set to False if the matrix and the vectors are already normalized (default: True)

    Returns
    -------
    array
        an array of size (len(bins) - 1) with the values of the histogram
    """
    if normalize:
        matrix = embeddings.matrix.normalize()
    else:
        matrix = embeddings.matrix

    hist = np.array([0] * (len(bins) - 1))
    for i in range(len(embeddings.words) - 1):
        vector = matrix[i]
        hist += np.histogram(distance(vector, matrix[i + 1:], normalize=False), bins=bins)[0]

    return hist


# ########################################
# t-SNE
def tsne(embeddings):
    """Create a 2d projections of the embeddings using t-SNE

    Parameters
    ----------
    embeddings: an instance of Embeddings
        Instance of :class:`mangoes.Embeddings` to project
    """

    try:
        matrix = embeddings.matrix.toarray()
    except AttributeError:
        # already dense
        matrix = embeddings.matrix

    import sklearn.manifold
    model = sklearn.manifold.TSNE()
    return model.fit_transform(matrix)
