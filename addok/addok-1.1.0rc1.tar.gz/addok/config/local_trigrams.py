from addok.config.default import (PROCESSORS_PYPATHS, INDEXERS_PYPATHS,
                                  RESULTS_COLLECTORS_PYPATHS)
from addok.config.local import *  # noqa

RESULTS_COLLECTORS_PYPATHS.remove('addok.helpers.collectors.extend_results_reducing_tokens')  # noqa
RESULTS_COLLECTORS_PYPATHS += [
    'addok_trigrams.extend_results_removing_numbers',
    'addok_trigrams.extend_results_removing_one_whole_word',
    'addok_trigrams.extend_results_removing_successive_trigrams',
]
PROCESSORS_PYPATHS += [
    'addok_trigrams.trigramize',
]
INDEXERS_PYPATHS.remove('addok.pairs.PairsIndexer')
INDEXERS_PYPATHS.remove('addok.autocomplete.EdgeNgramIndexer')

REDIS = {
    'host': 'localhost',
    'port': 6379,
    'db': 3
}
