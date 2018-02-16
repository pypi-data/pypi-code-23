import numpy as np
import tensorflow as tf

from sklearn.utils.murmurhash import murmurhash3_32

SEEDS = [
    179424941, 179425457, 179425907, 179426369,
    179424977, 179425517, 179425943, 179426407,
    179424989, 179425529, 179425993, 179426447,
    179425003, 179425537, 179426003, 179426453,
    179425019, 179425559, 179426029, 179426491,
    179425027, 179425579, 179426081, 179426549
]


class BloomEmbedding():
    def __init__(self, num_embeddings, compression_ratio=0.2, num_hash_functions=4, padding_idx=0):
        self.num_embeddings = num_embeddings
        self.compression_ratio = compression_ratio
        self.num_hash_functions = num_hash_functions
        self.padding_idx = padding_idx
        self.compressed_num_embeddings = int(compression_ratio * num_embeddings)

        if num_hash_functions > len(SEEDS):
            raise ValueError("Too many hash functions")

        self._masks = SEEDS[:self.num_hash_functions]

        self._hashes = None
        self._offsets = None

    def _get_hashed_indices(self, original_indices):

        def _hash(x, seed):
            result = murmurhash3_32(x, seed=seed)
            #result[self.padding_idx] = 0

            return result % self.compressed_num_embeddings

        if self._hashes is None:
            indices = np.arange(self.num_embeddings, dtype=np.int32)
            hashes = np.stack([_hash(indices, seed) for seed in self._masks], axis=1).astype(np.int64)

            #assert hashes[self.padding_idx].sum() == 0

            self._hashes = tf.convert_to_tensor(hashes, dtype=tf.int64)

        hashed_indices = tf.gather(self._hashes, original_indices, axis=0)

        return hashed_indices

    def forward(self, indices):
        hashed_indices = self._get_hashed_indices(indices)

        return hashed_indices



class AdvancedBloomEmbedding():
    def __init__(self, num_embeddings, embedding_dim, compression_ratio=0.2, num_hash_functions=1, padding_idx=0):
        self.num_embeddings = num_embeddings
        self.embedding_dim = embedding_dim
        self.compression_ratio = compression_ratio
        self.num_hash_functions = num_hash_functions
        self.padding_idx = padding_idx
        self.compressed_num_embeddings = int(compression_ratio * num_embeddings)

        if num_hash_functions > len(SEEDS):
            raise ValueError("Too many hash functions")

        self._masks = SEEDS[:self.num_hash_functions]

        self.embeddings = tf.get_variable(name="embeddings", shape=[self.compressed_num_embeddings, embedding_dim])

        self._hashes = None
        self._offsets = None

    def _get_hashed_indices(self, original_indices):

        def _hash(x, seed):
            result = murmurhash3_32(x, seed=seed)
            result[self.padding_idx] = 0

            return result % self.compressed_num_embeddings

        if self._hashes is None:
            indices = np.arange(self.num_embeddings, dtype=np.int32)
            hashes = np.stack([_hash(indices, seed) for seed in self._masks], axis=1).astype(np.int64)

            assert hashes[self.padding_idx].sum() == 0

            self._hashes = tf.convert_to_tensor(hashes, dtype=tf.int64)

        hashed_indices = tf.gather(self._hashes, original_indices, axis=0)

        return hashed_indices

    def forward(self, indices):
        shape = tf.shape(indices)

        hashed_indices = self._get_hashed_indices(indices)

        with tf.device("/cpu:0"):
            embedding = tf.nn.embedding_lookup(params=self.embeddings, ids=hashed_indices)
            embedding = tf.reduce_sum(embedding, axis=2)
            #TODO: reshape?

            return embedding
