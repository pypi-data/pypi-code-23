from string import ascii_uppercase, ascii_lowercase, digits
from enpc_aligner.IBM2_func import _train_IBM2, show_matrix
import re
from math import ceil, floor
from operator import itemgetter
from matplotlib.pyplot import plot, show, title, xlim, ylim, xlabel, ylabel, xticks, legend, matshow
from numpy import zeros, ones, infty

OCCUR_MIN = 4
FREQ_STEP = 0.001
FREQ_MAX = 0.002	# temps que l'incertitude sur la position du mot correspondant dans le texte d'en face est inférieur à l'écart entre 2 occurences.
FREQ_RATIO = 1.25
DTW_FACTOR = 1
BEGINNING_THRESHOLD = infty
BOOTSTRAP_FREQ = 0.005
LOG = False

FR_WORD_RE = r"[\w-]+'?"
EN_WORD_RE = r"'?[\w-]+"
SENTENCE_RE = r'[^ ]+"?[^\.\?!;:…"]+[\.\?!;:…"]+'
PARAGRAPH_RE = r"[^\n]*\w[^\n]*"
EMPTY_PAR_RE = r"[^ ].*[^ ]"

def paragraphs(text):
	return re.findall(PARAGRAPH_RE, text)
def sentences(paragraph):
	sen = re.findall(SENTENCE_RE, paragraph)
	if sen:
		return sen
	else:
		return re.findall(EMPTY_PAR_RE, paragraph)

def words(sentence, WORD_RE):
	return re.findall(WORD_RE, sentence if "'" not in sentence else sentence.replace("n't", " not"))

def _clean(word):
	return word.lower()

def clean(element):
	assert (type(element) is str or type(element) is list), "you can clean strings or lists only, {} given".format(type(element))
	return (
		_clean(element) if type(element) is str else
		[clean(subelement) for subelement in element]
	)

def print_text(text):
	print('\n\n'.join(['\n'.join([str(sentence) for sentence in paragraph]) for paragraph in text]))

def parse(text, language):
	WORD_RE = FR_WORD_RE if language == "french" else EN_WORD_RE
	original_text = [sentences(paragraph) for paragraph in paragraphs(text)]
	clean_text = [[clean(words(sentence, WORD_RE)) for sentence in paragraph] for paragraph in original_text]

	return original_text, clean_text

def read_example(instance, language):
	with open("../examples/{}/{}.txt".format(language, instance), "r") as text_file:
	    text = "\n".join([line for line in text_file])

	return parse(text, language)

def process(clean_text):
	word_indices = {}
	word_freq = {}
	word_offset = 0
	sen_offset = 0
	for id_par, par in enumerate(clean_text):
		word_offset_in_par = 0
		for id_sen, sen in enumerate(par):
			for id_word, word in enumerate(sen):
				indices = ((id_par, id_sen, id_word), word_offset_in_par, sen_offset, word_offset)
				if word not in word_indices:
					word_indices[word] = [indices]
				else:
					word_indices[word].append(indices)
				word_offset+=1
				word_offset_in_par+=1
			sen_offset+=1
	nb_words = word_offset
	nb_sen = sen_offset
	recency_vect = {}
	for word, indices_list in word_indices.items():
		recency_vect[word] = [indices_list[0][3]/nb_words]
		for idx in range(1, len(indices_list)):
			recency_vect[word].append((indices_list[idx][3]-indices_list[idx-1][3])/nb_words)
		recency_vect[word].append(1-indices_list[-1][3]/nb_words)

	for word, indices in word_indices.items():
		word_freq[word] = len(indices)/nb_words

	freq_ranking = sorted([(word, freq) for word, freq in word_freq.items()], key=itemgetter(1))

	return word_indices, recency_vect, word_freq, freq_ranking, nb_words, nb_sen

def compare_recency(en_word, fr_word, en_recency, fr_recency):
	plot(list(range(len(en_recency))), en_recency, label=en_word)
	plot(list(range(len(fr_recency))), fr_recency, label=fr_word)
	title("Vecteur de récence")
	xlabel("Indice de portions correspondantes")
	ylabel("Longueur relative de portion")
	legend()
	show()

mu = lambda a, b: abs(a-b)

def _dtw(rec1, rec2, freq):
	n, m = len(rec1), len(rec2)
	warp = infty*ones((n, m))	# les 1 font office de +infinity
	warp_ancestor = (zeros((n, m), dtype=int), zeros((n, m), dtype=int))
	warp[0, 0] = mu(rec1[0], rec2[0])
	warp_ancestor[0][0, 0] = -1
	warp_ancestor[1][0, 0] = -1
	warp[1, 0] = mu(rec2[0], rec1[0]+rec1[1])
	warp_ancestor[0][1, 0] = -1
	warp_ancestor[1][1, 0] = -1
	warp[0, 1] = mu(rec1[0], rec2[0]+rec2[1])
	warp_ancestor[0][0, 1] = -1
	warp_ancestor[1][0, 1] = -1
	k = (1 if freq <= FREQ_STEP else 2)
	for i in range(1, n):
		for j in range(max(1, ceil((i-1)/2), m-2*(n-i)+1), min(2*i+2, m-floor((n-i)/2))):
			minimum = [warp[i-1, j-1]+mu(rec1[i], rec2[j]), (i-1, j-1)]
			for l in range(1, k):
				if i >= 1+l:
					cost = warp[i-1-l, j-1]+mu(sum([rec1[t] for t in range(i-l, i+1)]), rec2[j])
					if cost < minimum[0]:
						minimum = [cost, (i-1-l, j-1)]
				else:
					break
			for l in range(1, k+1):
				if j >= 1+l:
					cost = warp[i-1, j-1-l]+mu(rec1[i], sum([rec2[t] for t in range(j-l, j+1)]))
					if cost < minimum[0]:
						minimum = [cost, (i-1, j-1-l)]
				else:
					break
			warp[i, j] = minimum[0]
			warp_ancestor[0][i, j], warp_ancestor[1][i, j] = minimum[1]
	return warp[n-1, m-1]/freq**DTW_FACTOR, warp_ancestor, warp

def dtw(word1, word2, rec1, rec2, freq, threshold, graph=False, log=False, matrix=False):
	value, warp_ancestor, warp = _dtw(rec1, rec2, freq)
	n, m = len(rec1), len(rec2)
	if  value <= threshold:
		backtracking = [(n-1, m-1)]
		warp[n-1][m-1] = 0
		while backtracking[-1] != (-1, -1):
			backtracking.append((warp_ancestor[0][backtracking[-1]], warp_ancestor[1][backtracking[-1]]))
			warp[backtracking[-1][0]][backtracking[-1][1]] = 0
		backtracking.reverse()
		if log:
			print(word1, "|", word2, "(", freq, "):", value)
		if matrix:
			matshow(warp)
			title("Calcul de distance par programmation dynamique")
			xlabel('Récence du mot anglais "{}"'.format(word1))
			ylabel('Récence du mot français "{}"'.format(word2))
			show()
		if graph:
			adjustedrec1 = [sum([rec1[k] for k in range(backtracking[idx-1][0]+1, backtracking[idx][0]+1)]) for idx in range(1, len(backtracking))]
			adjustedrec2 = [sum([rec2[k] for k in range(backtracking[idx-1][1]+1, backtracking[idx][1]+1)]) for idx in range(1, len(backtracking))]
			plot(adjustedrec1, label=word1)
			plot(adjustedrec2, label=word2)
			title("Correspondance par dilatation temporelle")
			xlabel("Indice de portion entre occurences")
			ylabel("Longueur relative de portion")
			legend()
			show()
		return value, backtracking[1:-1]
	else:
		return value, None


def filter_smooth(match_list):	# the list must be ordered
	assert match_list, "Aucun match trouvé"
	filtered_match_list = [match_list[0]]
	removed = []
	for i in range(1, len(match_list)-1):	# borne par 10 la dérivée disrète
		if abs((filtered_match_list[-1][1][3]+match_list[i+1][1][3])/2-match_list[i][1][3]) < 10*abs(match_list[i+1][0][3]-filtered_match_list[-1][0][3])/2:
			filtered_match_list.append(match_list[i])
		else:
			removed.append(match_list[i])
	filtered_match_list.append(match_list[-1])
	return filtered_match_list, removed

def filter_per_par(match_list):	# the list must be ordered
	assert match_list, "Aucun match trouvé"
	filtered_match_list = [match_list[0]]
	removed = []
	for i in range(1, len(match_list)-1):	# check that paragraph number is increasing
		if filtered_match_list[-1][1][0][0] <= match_list[i][1][0][0] <= match_list[i+1][1][0][0]:
			filtered_match_list.append(match_list[i])
		else:
			removed.append(match_list[i])
	return filtered_match_list, removed

def filter_non_bijective_matches(match_list, en_clean_text, fr_clean_text):
	en_match = {}
	fr_match = {}
	filtered_match_list = []
	removed = []
	for match in match_list:
		en_word = en_clean_text[match[0][0][0]][match[0][0][1]][match[0][0][2]]
		fr_word = fr_clean_text[match[1][0][0]][match[1][0][1]][match[1][0][2]]
		if en_word not in en_match:
			en_match[en_word] = [[match], fr_word]
		elif fr_word == en_match[en_word][1]:
			en_match[en_word][0].append(match)
		elif match[2] < en_match[en_word][0][0][2]:
				en_match[en_word] = [[match], fr_word]
		if fr_word not in fr_match:
			fr_match[fr_word] = [[match], en_word]
		elif en_word == fr_match[fr_word][1]:
			fr_match[fr_word][0].append(match)
		elif match[2] < fr_match[fr_word][0][0][2]:
			fr_match[fr_word] = [[match], en_word]
	for en_word, [match_list, fr_word] in en_match.items():
		if en_word == fr_match[fr_word][1]:
			filtered_match_list.extend(match_list)
		else:
			removed.extend(match_list)

	return sorted(filtered_match_list, key=lambda x: x[0][3]), removed

def estimate_threshold(en_freq_ranking, fr_freq_ranking, en_recency_vect, fr_recency_vect, en_word_indices, fr_word_indices, en_nb_words, kept_freq):
	match_list = []
	occur_min = OCCUR_MIN
	while not match_list and occur_min >= 1:
		en_nb_different_words = len(en_freq_ranking)
		fr_nb_different_words = len(fr_freq_ranking)
		bound_inf, bound_sup = 0, 0
		idx_freq_min, idx_freq_max = 0, en_nb_different_words-1

		while en_freq_ranking[idx_freq_min][1]*en_nb_words < occur_min:	# au moins 4 occurrences 0.00023
			idx_freq_min+=1
		while en_freq_ranking[idx_freq_max][1] > FREQ_MAX:
			idx_freq_max-=1

		while idx_freq_min <= idx_freq_max:
			en_word, freq = en_freq_ranking[idx_freq_min]
			idx_freq_min+=1
			if freq*en_nb_words > occur_min:
				break
			while bound_inf < fr_nb_different_words-1 and fr_freq_ranking[bound_inf][1] < freq/FREQ_RATIO:
				bound_inf+=1
			while bound_sup < fr_nb_different_words-1 and fr_freq_ranking[bound_sup][1] <= freq*FREQ_RATIO:
				bound_sup+=1
			for idx in range(bound_inf, bound_sup):
				fr_word = fr_freq_ranking[idx][0]
				value, path = dtw(en_word, fr_word, en_recency_vect[en_word], fr_recency_vect[fr_word], freq, BEGINNING_THRESHOLD)
				if path:
					for match in path:
						match_list.append((en_word_indices[en_word][match[0]], fr_word_indices[fr_word][match[1]], value, freq))
		match_list.sort(key=itemgetter(2))
		match_list = match_list[:min(len(match_list), ceil(en_nb_words*kept_freq))]	# calibrer pour garder les 16 meilleures matches parmis les mots de 4 lettres pour ce texte de 16 000 mots
		occur_min-=1
	threshold = match_list[-1][2]
	print("THRESHOLD :", threshold)
	return threshold, match_list, idx_freq_min, idx_freq_max, bound_inf, bound_sup

def matching_layer(threshold, match_list, en_freq_ranking, fr_freq_ranking, en_recency_vect, fr_recency_vect, en_word_indices, fr_word_indices, bound_inf, bound_sup, en_clean_text, fr_clean_text):
	en_nb_different_words = len(en_freq_ranking)
	fr_nb_different_words = len(fr_freq_ranking)

	for en_word, freq in en_freq_ranking:
		#if freq >= FREQ_STEP:
		#	adjusted_freq_ratio = 2*FREQ_RATIO
		while bound_inf < fr_nb_different_words-1 and fr_freq_ranking[bound_inf][1] < freq/FREQ_RATIO:	#*nb_fr_words/nb_en_words
			bound_inf+=1
		while bound_sup < fr_nb_different_words-1 and fr_freq_ranking[bound_sup][1] <= freq*FREQ_RATIO:	#*nb_fr_words/nb_en_words
			bound_sup+=1
		for idx in range(bound_inf, bound_sup):
			fr_word = fr_freq_ranking[idx][0]
			value, path = dtw(en_word, fr_word, en_recency_vect[en_word], fr_recency_vect[fr_word], freq, threshold, log=True)
			if path:
				for match in path:
					match_list.append((en_word_indices[en_word][match[0]], fr_word_indices[fr_word][match[1]], value, freq))

	match_list.sort(key=lambda x: x[0][3])	# sort on word index in text 1

def filtration_layer(match_list, en_clean_text, fr_clean_text, log=False):
	if log:
		print("Avant filtration :", len(match_list))
		plot([item[0][3] for item in match_list], [item[1][3] for item in match_list], label="sans filtration")

	match_list, non_bijective_removed = filter_non_bijective_matches(match_list, en_clean_text, fr_clean_text)
	if log:
		print("Après filtration des matches non bijectifs :", len(match_list))
		plot([item[0][3] for item in match_list], [item[1][3] for item in match_list], label="(1) par bijection")

	match_list, smooth_removed = filter_smooth(match_list)
	if log:
		print("Après filtration par lissage :", len(match_list))
		plot([item[0][3] for item in match_list], [item[1][3] for item in match_list], label="(2) par lissage")

	match_list, per_par_removed = filter_per_par(match_list)
	if log:
		print("Après filtration par paragraphe croissant :", len(match_list))
		plot([item[0][3] for item in match_list], [item[1][3] for item in match_list], label="(3) par paragraphe croissant")
		title("Alignement après filtration (1), (2) puis (3)")
		xlabel("Indice de mot anglais")
		ylabel("Indice de mot français")
		legend()
		show()

	if log:
		print("Non bijective matches removed")
		for match in non_bijective_removed:
			print(en_clean_text[match[0][0][0]][match[0][0][1]][match[0][0][2]], "|", fr_clean_text[match[1][0][0]][match[1][0][1]][match[1][0][2]])
		print("Smooth removed")
		for match in smooth_removed:
			print(en_clean_text[match[0][0][0]][match[0][0][1]][match[0][0][2]], "|", fr_clean_text[match[1][0][0]][match[1][0][1]][match[1][0][2]])
		print("Per par removed")
		for match in per_par_removed:
			print(en_clean_text[match[0][0][0]][match[0][0][1]][match[0][0][2]], "|", fr_clean_text[match[1][0][0]][match[1][0][1]][match[1][0][2]])

	return match_list

def zipf_curve(freq_ranking, nb_words, label, show=True):
	freqs = [freq_ranking[0][1]]
	zipf_law = [1]
	for word, freq in freq_ranking[1:]:
		if freqs[-1] == freq:
			zipf_law[-1]+=1
		else:
			freqs.append(freq)
			zipf_law.append(1)
	nb_occurs = [freq*nb_words for freq in freqs]
	if show:
		line = plot(nb_occurs, zipf_law, label=label)

	return nb_occurs, zipf_law, line

def draw_occurences_chart(en_freq_ranking, fr_freq_ranking, en_nb_words, fr_nb_words):
	en_nb_occurs, en_zipf_law, en_line = zipf_curve(en_freq_ranking, en_nb_words, "anglais")
	fr_nb_occurs, fr_zipf_law, fr_line = zipf_curve(fr_freq_ranking, fr_nb_words, "français")
	inverse_square = plot([occurs for occurs in en_nb_occurs], [2000/occurs**2 for occurs in en_nb_occurs], ls=":", label=r"$\dfrac{1}{n^2}$")
	plot([OCCUR_MIN, OCCUR_MIN], [0, 1000], ls="--")
	plot([FREQ_MAX*en_nb_words, FREQ_MAX*en_nb_words], [0, 1000], ls="--")
	legend()
	title("Effectif avec même nombre d'occurrences")
	xlabel("Nombre d'occurrences d'un mot")
	ylabel("Nombre de mots")
	xlim(0, FREQ_MAX*en_nb_words+OCCUR_MIN)
	ylim(0, 100)
	show()

def apply_IBM(match_list, en_clean_text, fr_clean_text, log=False):
	corpus_IBM2 = []
	for match in match_list[:4]:
		if (en_clean_text[match[0][0][0]][match[0][0][1]], fr_clean_text[match[1][0][0]][match[1][0][1]]) not in corpus_IBM2:
			corpus_IBM2.append((en_clean_text[match[0][0][0]][match[0][0][1]], fr_clean_text[match[1][0][0]][match[1][0][1]]))
	t_IBM2, a_IBM2 = _train_IBM2(corpus_IBM2, loop_count=1000)

	len(t_IBM2)
	len(a_IBM2)

	for (es, fs) in corpus_IBM2:
		#max_a = viterbi_alignment(es, fs, t_IBM2, a_IBM2).items()
		m = len(es)
		n = len(fs)
		args = (es, fs, t_IBM2, a_IBM2)
		if log:
			print(show_matrix(*args))

lin_interp = lambda t, a, b, f_a, f_b: f_a+(f_b-f_a)*(t-a)/(b-a)

def align_paragraphs(en_clean_text, fr_clean_text):
	en_word_indices, en_recency_vect, en_word_freq, en_freq_ranking, en_nb_words, en_nb_sen = process(en_clean_text)
	fr_word_indices, fr_recency_vect, fr_word_freq, fr_freq_ranking, fr_nb_words, fr_nb_sen = process(fr_clean_text)

	threshold, match_list, idx_freq_min, idx_freq_max, bound_inf, bound_sup = estimate_threshold(en_freq_ranking, fr_freq_ranking, en_recency_vect, fr_recency_vect, en_word_indices, fr_word_indices, en_nb_words, BOOTSTRAP_FREQ)
	matching_layer(threshold, match_list, en_freq_ranking[idx_freq_min: idx_freq_max+1], fr_freq_ranking, en_recency_vect, fr_recency_vect, en_word_indices, fr_word_indices, bound_inf, bound_sup, en_clean_text, fr_clean_text)
	match_list = filtration_layer(match_list, en_clean_text, fr_clean_text)
	# word_matches = [[(en_clean_text[match[0][0][0]][match[0][0][1]][match[0][0][2]], match[0][0][0], match[0][0][1]), (fr_clean_text[match[1][0][0]][match[1][0][1]][match[1][0][2]]], match[1][0][0], match[1][0][1]), match[2]] for match in match_list]

	aligned_matches = [(0, 0)]+[(match[0][0][0], match[1][0][0]) for match in match_list]+[(len(en_clean_text)-1, len(fr_clean_text)-1)]
	aligned_paragraphs = []
	for i in range(1, len(aligned_matches)):
		aligned_paragraphs.append((aligned_matches[i-1][0], aligned_matches[i-1][1]))
		for j in range(aligned_matches[i-1][0]+1, aligned_matches[i][0]):
			aligned_paragraphs.append((j, int(round(lin_interp(j, aligned_matches[i-1][0], aligned_matches[i][0], aligned_matches[i-1][1], aligned_matches[i][1])))))
	aligned_paragraphs.append((aligned_matches[len(aligned_matches)-1][0], aligned_matches[len(aligned_matches)-1][1]))
	clustered_aligned_par = [([aligned_paragraphs[0][0]], [aligned_paragraphs[0][1]])]
	for idx in range(1, len(aligned_paragraphs)):
		if aligned_paragraphs[idx][0] == aligned_paragraphs[idx-1][0] and aligned_paragraphs[idx][1] != aligned_paragraphs[idx-1][1]:
			clustered_aligned_par[-1][1].extend([id for id in range(aligned_paragraphs[idx-1][1]+1, aligned_paragraphs[idx][1]+1)])
		elif aligned_paragraphs[idx][0] != aligned_paragraphs[idx-1][0] and aligned_paragraphs[idx][1] == aligned_paragraphs[idx-1][1]:
			clustered_aligned_par[-1][0].append(aligned_paragraphs[idx][0])
		elif aligned_paragraphs[idx][0] != aligned_paragraphs[idx-1][0] and aligned_paragraphs[idx][1] != aligned_paragraphs[idx-1][1]:
			clustered_aligned_par.append(([aligned_paragraphs[idx][0]], [id for id in range(aligned_paragraphs[idx-1][1]+1, aligned_paragraphs[idx][1]+1)]))

	return clustered_aligned_par, match_list
