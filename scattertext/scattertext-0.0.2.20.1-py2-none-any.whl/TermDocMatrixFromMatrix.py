from scipy.sparse import csr_matrix

from scattertext import TermDocMatrix, IndexStore, IndexStoreFromDict
from scattertext.indexstore import IndexStoreFromList


class DimensionMismatchException(Exception):
	pass


class TermDocMatrixFromMatrix(object):
	def __init__(self,
	             X,
	             y,
	             feature_vocabulary,
	             category_names,
	             unigram_frequency_path=None):
		'''
		Parameters
		----------
		X: sparse matrix, (docs X features)
		y: list, integer categories
		feature_vocabulary: dict (feat_name -> idx)
		category_names: list of category names
		unigram_frequency_path: str (see TermDocMatrix)
		'''

		if X.shape != (len(y), len(feature_vocabulary)):
			raise DimensionMismatchException('The shape of X is expected to be ' +
			                                 str((len(y), len(feature_vocabulary))) +
			                                 'but was actually: ' + str(X.shape))

		return TermDocMatrix(
			X=X.tocsr(),
			mX=csr_matrix(),
			y=y,
			term_idx_store=IndexStoreFromDict(feature_vocabulary),
			metadata_idx_store=IndexStore(),
			category_idx_store=IndexStoreFromList()
		)
