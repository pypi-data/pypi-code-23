"""Basic matchers.
"""

import os

import cPickle as pickle
import numpy as np
from scipy.spatial import distance

from owl.search import common

from annoy import AnnoyIndex


class ExactMatcher(common.BaseMatcher):
  """Matchers use common distance metric.
  """

  db_feats = None
  db_metadata = None
  matcher_protocol = common.MatchProtocol.EXACT

  def __init__(self, name, matcher_type, res_dir=None):
    super(ExactMatcher, self).__init__(name, matcher_type, res_dir)

  def prepare_database(self, db_items):
    """Load database.

    Args:
      db_items: a dictionary with keys:
      "metadata", a list of metadata for each item;
      "features": a numpy array of feature vectors, row basis.
    """
    self.db_feats = db_items["features"]
    self.db_metadata = db_items["metadata"]

  def match(self, query_items, top_nn=10, dist_func=None):
    """Do match to get top neighbors.

    Args:
      query_items: dict with "metadata" and "features".
      top_nn: number of neighbors to get.
      dist_func: custom distance function which takes two
      feature vectors and return a value.
    Returns:
      a 2d list where (i,j) element is the jth most similar item for ith query.
    """
    query_feats = query_items["features"]
    # Compute distance matrix.
    dist_mat = None
    if dist_func is None:
      if self.matcher_type == common.MatcherType.L2:
        dist_mat = distance.cdist(query_feats, self.db_feats, "euclidean")
      if self.matcher_type == common.MatcherType.L1:
        dist_mat = distance.cdist(query_feats, self.db_feats, "minkowski", 1)
    else:
      db_size = len(self.db_feats)
      query_size = len(query_feats)
      dist_mat = np.zeros((query_size, db_size), dtype=float)
      for qid in range(query_size):
        for did in range(db_size):
          dist_mat[qid, did] = dist_func(query_feats[qid], self.db_feats[did])
    # sort results.
    ranked_lists = np.argsort(dist_mat, axis=1)
    return ranked_lists[:, :top_nn]


class ANNMatcher(common.BaseMatcher):
  """Matcher using approximate nearest neighbors.
  """

  index_fn = None
  metadata_fn = None
  res_dir = None
  # list of metadata objects for all items.
  db_metadata = None
  # a row major matrix of feature vectors.
  db_feats = None
  db_index = None
  feat_dim = 0
  num_trees = 30
  match_protocol = common.MatchProtocol.APPROXIMATE

  def __init__(self, name, matcher_type, feat_dim, num_trees, res_dir=None):
    super(ANNMatcher, self).__init__(name, matcher_type, res_dir)
    self.index_fn = os.path.join(self.res_dir,
                                 "{}_annoy_ann.index".format(name))
    assert self.matcher_type in [
        common.MatcherType.L2, common.MatcherType.ANGULAR
    ], "current ann matcher only supports l2 or angular distance"
    # create index object.
    assert feat_dim > 0, "feature dimension can not be smaller than 0."
    self.feat_dim = feat_dim
    self.num_trees = num_trees
    if self.matcher_type == common.MatcherType.L2:
      self.db_index = AnnoyIndex(self.feat_dim, "euclidean")
    else:
      self.db_index = AnnoyIndex(self.feat_dim, "angular")
    self.metadata_fn = os.path.join(self.res_dir,
                                    self.matcher_name + ".metadata")

  def load_index(self):
    """Load index from file.
    """
    self.db_index.load(self.index_fn)
    print "db index loaded."
    with open(self.metadata_fn, "rb") as f:
      self.db_metadata = pickle.load(f)
      print "metadata loaded."

  def prepare_database(self, db_items):
    """Create index and save to file.

    Args:
      db_items: a dictionary with keys:
      "metadata", a list of metadata for each item, e.g. objectid.
      "features": a numpy array of feature vectors, row basis.
    """
    if db_items is None and os.path.exists(self.index_fn):
      self.load_index()
    else:
      self.db_metadata = db_items["metadata"]
      self.db_feats = db_items["features"]
      feat_num, feat_dim = self.db_feats.shape
      assert feat_dim == self.feat_dim, \
      "database feature dimension is not the same as index."
      # add items to index.
      print "start building ann index..."
      for i in range(feat_num):
        self.db_index.add_item(i, self.db_feats[i])
      # build index.
      # TODO(jiefeng): choose a proper number of tree.
      self.db_index.build(self.num_trees)
      print "db index built."
      self.db_index.save(self.index_fn)
      print "index file saved to {}".format(self.index_fn)
      with open(self.metadata_fn, "wb") as f:
        pickle.dump(self.db_metadata, f)
        print "metadata saved."

  def match(self, query_items, top_nn=10, dist_func=None):
    """Perform match on database for each query.

    Args:
      query_items: a dict with "metadata" and "features".
    Returns:
      a ranked list of db item ids.
    """
    query_feats = query_items["features"]
    query_size = query_feats.shape[0]
    print "start matching..."
    ranked_list = np.zeros((query_size, top_nn), dtype=int)
    for query_id, query_feat in enumerate(query_feats):
      # cur_nns: ([ids],[dists])
      cur_nns = self.db_index.get_nns_by_vector(
          query_feat, top_nn, include_distances=True)
      nn_ids, _ = cur_nns
      ranked_list[query_id] = np.array(nn_ids, dtype=int)
    print "matching done."
    return ranked_list
