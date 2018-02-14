#!/usr/bin/env python

from string import ascii_uppercase, ascii_lowercase, digits
import re
from math import ceil, floor
from operator import itemgetter
from matplotlib.pyplot import plot, show, title, xlim, ylim, xlabel, ylabel, xticks, legend, matshow
from numpy import zeros, ones, infty
from enpc_aligner.dtw import *

def try_example(instance):
    en_original_text, en_clean_text = read_example(instance, "english")
    en_word_indices, en_recency_vect, en_word_freq, en_freq_ranking, en_nb_words, en_nb_sen = process(en_clean_text)
    print("Longueur du texte {} ({}): {} mots.".format(instance, "english", en_nb_words))
    print("Nombres de mots différents : {}.".format(len(en_word_indices)))
    fr_original_text, fr_clean_text = read_example(instance, "french")
    fr_word_indices, fr_recency_vect, fr_word_freq, fr_freq_ranking, fr_nb_words, fr_nb_sen = process(fr_clean_text)
    print("Longueur du texte {} ({}): {} mots.".format(instance, "french", fr_nb_words))
    print("Nombres de mots différents : {}.".format(len(fr_word_indices)))

    draw_occurences_chart(en_freq_ranking, fr_freq_ranking, en_nb_words, fr_nb_words)

    compare_recency("but", "mais", en_recency_vect["but"], fr_recency_vect["mais"])
    dtw("but", "mais", en_recency_vect["but"], fr_recency_vect["mais"], en_word_freq["but"], infty, True, True)
    compare_recency("king", "roi", en_recency_vect["king"], fr_recency_vect["roi"])
    dtw("king", "roi", en_recency_vect["king"], fr_recency_vect["roi"], en_word_freq["king"], infty, True, True)
    compare_recency("prince", "prince", en_recency_vect["prince"], fr_recency_vect["prince"])
    dtw("prince", "prince", en_recency_vect["prince"], fr_recency_vect["prince"], en_word_freq["prince"], infty, True, True)
    compare_recency("why", "pourquoi", en_recency_vect["why"], fr_recency_vect["pourquoi"])
    dtw("why", "pourquoi", en_recency_vect["why"], fr_recency_vect["pourquoi"], en_word_freq["why"], infty, True, True)

    print("Estimating threshold distance value...")
    threshold, match_list, idx_freq_min, idx_freq_max, bound_inf, bound_sup = estimate_threshold(en_freq_ranking, fr_freq_ranking, en_recency_vect, fr_recency_vect, en_word_indices, fr_word_indices, en_nb_words, BOOTSTRAP_FREQ)
    for match in match_list:
    	print(en_clean_text[match[0][0][0]][match[0][0][1]][match[0][0][2]], "|", fr_clean_text[match[1][0][0]][match[1][0][1]][match[1][0][2]], "(", match[3], "):", match[2])
    matching_layer(threshold, match_list, en_freq_ranking[idx_freq_min: idx_freq_max+1], fr_freq_ranking, en_recency_vect, fr_recency_vect, en_word_indices, fr_word_indices, bound_inf, bound_sup)
    print("Nombre de phrases en anglais :", en_nb_sen)
    print("Nombre de phrases en français :", fr_nb_sen)
    filtration_layer(match_list, en_clean_text, fr_clean_text, True)

    light_match_list = [match_list[0]]
    for match in match_list[1:]:
    	if match[0][2] != light_match_list[-1][0][2]:
    		light_match_list.append(match)

    for match in light_match_list:
    	print(en_original_text[match[0][0][0]][match[0][0][1]])
    	print(fr_original_text[match[1][0][0]][match[1][0][1]])
    	print("\n")
    print("Nombre de phrases alignées :", len(light_match_list))

    apply_IBM(match_list, en_clean_text, fr_clean_text, True)


try_example("le-petit-prince--antoine-de-saint-exupery")
#try_example("bible")   # need for reformatting : remove beginning of each line
#try_example("pinocchio")   # need for reformatting : \n breaks sentences
