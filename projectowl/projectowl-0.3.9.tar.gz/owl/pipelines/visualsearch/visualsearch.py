"""Visual search pipeline.
"""

import os
import time
import sys

import cPickle as pickle
import numpy as np

from sklearn.preprocessing import normalize

from jinja2 import Environment, FileSystemLoader

from owl.data import common
from owl.data import img_tools
from owl.data import mongo_manager
from owl.features import obj_feat_extractor
from owl.processors import dim_reductor
from owl.search import common as search_common
from owl.search import simple_matchers
from owl.pipelines.common import PipelineMode


class OneFeatVisualSearcher(object):
  """A single feature based visual search object.

  Used for both development and deployment.

  1) read in files and organize into database and query.
  2) compute features and save to database:
  [img_fn, label, type, feat1, feat2, ...].
  3) reduce feature dimension if too high (x00~1000+) and save to database.
  4) run matching.
  5) evalute.
  All db involved: [task_name]_db.raw_feats, [task_name]_db.compressed_feats,
                   [task_name]_query.raw_feats, [task_name]_query.compressed_feats.

    Attributes:
      res_dir: result directory.
  """

  res_dir = None
  logger = None
  task_name = ""
  mode = PipelineMode.DEVELOPMENT
  # db name for database.
  task_db_db_name = ""
  # db name for query.
  task_query_db_name = ""
  target_feat_name = ""
  target_feat_dim = 0
  # list of items.
  db_items = []
  query_items = []
  # {feat_name: feat_matrix}
  db_feats = {}
  query_feats = {}
  # ranked list of db ids for each query.
  ranked_lists = None
  # feature extraction.
  feat_extractor = None
  feat_compute_batch_size = 10
  # feature dim reduction.
  use_feat_compressor = False
  feat_compress_batch_size = 10
  compress_feat_dim = 128
  train_feat_compressor = False
  feat_compressor = None
  # matching.
  matcher = None
  match_protocol = search_common.MatchProtocol.APPROXIMATE
  num_trees = 100

  def __init__(self, task_name, res_dir):
    self.task_name = task_name
    self.task_db_db_name = "{}_db".format(self.task_name)
    self.task_query_db_name = "{}_query".format(self.task_name)
    self.res_dir = res_dir
    log_fn = os.path.join(res_dir, "log.txt")
    self.logger = common.get_logger("visualsearchlogger", log_fn)

  def clean_db(self):
    """Remove all related database.
    """
    db_man = mongo_manager.MongoManager()
    db_man.connect()
    db_man.delete_db(self.task_db_db_name)
    db_man.delete_db(self.task_query_db_name)

  def load_items_from_db(self):
    """Load data from local db.
    """
    # load db items.
    self.db_items = []
    item_db = mongo_manager.MongoManager()
    item_db.connect(db_name=self.task_db_db_name, collection_name="items")
    db_cursor = item_db.get_scan_cursor()
    for db_item in db_cursor:
      self.db_items.append(db_item)
    print "{} db items loaded from db.".format(len(self.db_items))
    if self.mode == PipelineMode.DEVELOPMENT:
      # load query items.
      self.query_items = []
      item_db.switch_db_collection(self.task_query_db_name, "items")
      query_cursor = item_db.get_scan_cursor()
      for query_item in query_cursor:
        self.query_items.append(query_item)
      print "{} query items loaded from db.".format(len(self.query_items))
    item_db.disconnect()

  def load_feats_from_db(self, raw_feat=False):
    """Load features from db.

    At the same time, load item with the same order.
    """

    def load_feats_items_from_db(item_db, feat_db):
      """load features and items from db.

      Args:
        item_db: item db object.
        feat_db: feat db object.
      Returns:
        items: list of items
        feats: feature ndarray.
      """
      items = []
      db_cursor = feat_db.get_scan_cursor()
      total_item_count = db_cursor.count()
      feats = np.zeros((total_item_count, self.target_feat_dim))
      for db_id, db_feat_item in enumerate(db_cursor):
        db_item_id = db_feat_item["_id"]
        db_feat = np.array(db_feat_item[self.target_feat_name]).reshape(1, -1)
        feats[db_id] = db_feat
        cur_item = item_db.query(value_list=[db_item_id])[0]
        items.append(cur_item)
        if len(items) % 1000 == 0:
          print "loaded {}/{} items".format(len(items), total_item_count)
      return items, feats

    self.logger.info("loading features from db...")
    # load db data.
    item_db = mongo_manager.MongoManager()
    item_db.connect(db_name=self.task_db_db_name, collection_name="items")
    feat_db = mongo_manager.MongoManager()
    if not raw_feat:
      feat_db.connect(
          db_name=self.task_db_db_name, collection_name="compressed_feats")
    else:
      feat_db.connect(
          db_name=self.task_db_db_name, collection_name="raw_feats")
    self.db_items, self.db_feats = load_feats_items_from_db(item_db, feat_db)

    if self.mode == PipelineMode.DEVELOPMENT:
      # load query data.
      item_db.switch_db_collection(
          db_name=self.task_query_db_name, collection_name="items")
      if not raw_feat:
        feat_db.switch_db_collection(
            db_name=self.task_query_db_name,
            collection_name="compressed_feats")
      else:
        feat_db.switch_db_collection(
            db_name=self.task_query_db_name, collection_name="raw_feats")
      self.query_items, self.query_feats = load_feats_items_from_db(item_db,
                                                                    feat_db)

    item_db.disconnect()
    feat_db.disconnect()
    self.logger.info("features loaded from db")

  def read_data_from_files(self, img_folder, img_exts):
    """Input image data.

    Args:
      img_folder: folder contains image files.
    If has subfolders, each is treated as a category with folder name.
    """
    # read all image files.
    img_fns, img_labels, _ = common.list_img_files(img_folder, img_exts)
    # split into query and database.
    db_ids, _, query_ids = common.split_train_val_test(
        img_labels, train_ratio=0.8, test_ratio=0.2)
    self.logger.info("{} db files and {} query files found.".format(
        len(db_ids), len(query_ids)))
    # save db item info.
    item_db = mongo_manager.MongoManager()
    item_db.connect(db_name=self.task_db_db_name, collection_name="items")
    item_db.delete_collection()
    for i, db_id in enumerate(db_ids):
      cur_db_item = {"img_fn": img_fns[db_id], "label": img_labels[db_id]}
      item_db.add(cur_db_item)
      if i % 100 == 0:
        self.logger.info("{}/{} db items added.".format(i, len(db_ids)))
    self.logger.info("all db items added to db.")
    # save query item info.
    item_db.switch_db_collection(self.task_query_db_name, "items")
    item_db.delete_collection()
    for i, query_id in enumerate(query_ids):
      cur_query_item = {
          "img_fn": img_fns[query_id],
          "label": img_labels[query_id]
      }
      item_db.add(cur_query_item)
      if i % 100 == 0:
        self.logger.info("{}/{} query items added.".format(i, len(query_ids)))
    self.logger.info("all query items added to db.")
    item_db.disconnect()

  def compute_feats(self):
    """[DEV] Compute features for all images.

    Args:
      features: feature extractors.
      batch_size: image batch to process.
    """

    def compute_raw_feats_(raw_feat_db, items):
      """compute raw features for a specific db.

      Args:
        raw_feat_db: db object for raw features.
        items: list of items.
      """
      startt = time.time()
      # loop over items.
      for idx in range(0, len(items), self.feat_compute_batch_size):
        try:
          batch_items = items[idx:idx + self.feat_compute_batch_size]
          rgb_imgs = []
          # group images.
          for item in batch_items:
            img_bin = img_tools.read_img_bin(item["img_fn"])
            img_arr = img_tools.img_bin_to_img_arr(img_bin)
            rgb_imgs.append(img_arr)
          # compute batch features.
          startt2 = time.time()
          batch_feats = self.feat_extractor.compute_batch(rgb_imgs)
          self.logger.info("batch feature extraction time: {}s".format(
              time.time() - startt2))
          # save feature to database.
          batch_feat_objs = []
          for item_id, item in enumerate(batch_items):
            cur_feat_obj = {}
            cur_feat_obj["_id"] = item["_id"]
            cur_feat_obj[self.target_feat_name] = batch_feats[item_id].tolist()
            batch_feat_objs.append(cur_feat_obj)
          raw_feat_db.add_many(batch_feat_objs)
          self.logger.info("database feature: {}/{}".format(
              min(idx + self.feat_compute_batch_size, len(items)), len(items)))
        except Exception as ex:
          self.logger.error("{}, skip one batch".format(
              common.get_detailed_error_msg(ex.message, sys.exc_info())))
          continue

      self.logger.info(
          "database feature extraction done. total time cost: {}s".format(
              time.time() - startt))

    # compute features for db.
    raw_feat_db = mongo_manager.MongoManager()
    raw_feat_db.connect(
        db_name=self.task_db_db_name, collection_name="raw_feats")
    raw_feat_db.delete_collection()
    compute_raw_feats_(raw_feat_db, self.db_items)

    # compute features for query.
    raw_feat_db.switch_db_collection("{}_query".format(self.task_name),
                                     "raw_feats")
    raw_feat_db.delete_collection()
    compute_raw_feats_(raw_feat_db, self.query_items)
    raw_feat_db.disconnect()

  def compress_feats(self):
    """[DEV] Compress features.
    """
    raw_feat_db = mongo_manager.MongoManager()
    raw_feat_db.connect(
        db_name=self.task_db_db_name, collection_name="raw_feats")
    if self.train_feat_compressor:
      db_item_cursor = raw_feat_db.get_scan_cursor()
      total_db_item_count = db_item_cursor.count()
      train_batch_size = min(self.feat_compress_batch_size,
                             total_db_item_count)
      self.logger.info("total db item to use for training compressor: {}".
                       format(total_db_item_count))
      db_raw_feats_batch = None
      batch_item_count = 0
      total_item_count = 0
      for db_item in db_item_cursor:
        cur_feat = np.array(db_item[self.target_feat_name])
        cur_feat = cur_feat.reshape(1, -1)
        batch_item_count += 1
        total_item_count += 1
        if db_raw_feats_batch is None:
          db_raw_feats_batch = cur_feat
        else:
          db_raw_feats_batch = np.vstack((db_raw_feats_batch, cur_feat))
        if batch_item_count >= train_batch_size:
          print "{}/{} db features loaded.".format(total_item_count,
                                                   total_db_item_count)
          print db_raw_feats_batch.shape
          self.feat_compressor.train(db_raw_feats_batch, False)
          print "dim reducer updated."
          db_raw_feats_batch = None
          batch_item_count = 0
    else:
      self.feat_compressor.save_load_model(to_save=False)

    def _compress_feats(raw_feat_db, compressed_feat_db):
      """Actually compress feats in a db.

      Args:
        raw_feat_db: raw feature db object.
        compressed_feat_db: compressed feat db object.
      """
      raw_item_cursor = raw_feat_db.get_scan_cursor()
      db_item_count = raw_item_cursor.count()
      cur_batch_size = min(self.feat_compress_batch_size, db_item_count)
      batch_item_count = 0
      processed_item_count = 0
      batch_feats = None
      batch_objs = []
      for item in raw_item_cursor:
        batch_item_count += 1
        processed_item_count += 1
        old_feat = np.array(item[self.target_feat_name]).reshape(1, -1)
        if batch_feats is None:
          batch_feats = old_feat
        else:
          batch_feats = np.vstack((batch_feats, old_feat))
        cur_obj = {"_id": item["_id"]}
        batch_objs.append(cur_obj)
        if batch_item_count >= cur_batch_size:
          new_feats = self.feat_compressor.transform(batch_feats)
          new_feats = normalize(new_feats, norm="l2")
          for idx, new_feat in enumerate(new_feats):
            batch_objs[idx][self.target_feat_name] = new_feat.tolist()
          # add to database.
          # TODO(jiefeng): use update to save storage?
          compressed_feat_db.add_many(batch_objs)
          self.logger.info("{}/{} compressed feature added to db.".format(
              processed_item_count, db_item_count))
          # clean.
          batch_item_count = 0
          batch_objs = []
          batch_feats = None
      self.logger.info("feature compression done.")

    # compress db features.
    self.logger.info("start compressing db features")
    raw_feat_db.switch_db_collection(
        db_name=self.task_db_db_name, collection_name="raw_feats")
    compressed_feat_db = mongo_manager.MongoManager()
    compressed_feat_db.connect(
        db_name=self.task_db_db_name, collection_name="compressed_feats")
    compressed_feat_db.delete_collection()
    _compress_feats(raw_feat_db, compressed_feat_db)
    # compress query features.
    self.logger.info("start compressing query features")
    raw_feat_db.switch_db_collection(
        db_name=self.task_query_db_name, collection_name="raw_feats")
    compressed_feat_db.switch_db_collection(
        db_name=self.task_query_db_name, collection_name="compressed_feats")
    compressed_feat_db.delete_collection()
    _compress_feats(raw_feat_db, compressed_feat_db)

    # clean.
    raw_feat_db.disconnect()
    compressed_feat_db.disconnect()

  def run_match(self):
    """[DEV] Perform matching between query and database.
    """
    self.logger.info("start matching...")
    # set database.
    if len(self.db_feats) == 0 or len(self.query_feats) == 0:
      self.load_feats_from_db(not self.use_feat_compressor)
    assert len(self.db_feats) > 0 and len(self.query_feats) > 0, \
      "db or query feature is empty"
    db_items = {"metadata": self.db_items}
    db_items["features"] = self.db_feats
    self.matcher.prepare_database(db_items)
    query_items = {"metadata": self.query_items}
    query_items["features"] = self.query_feats
    startt = time.time()
    self.ranked_lists = self.matcher.match(query_items, top_nn=20)
    self.logger.info("match time: {}s".format(time.time() - startt))
    self.logger.info("matching done.")

  def evaluate(self):
    """[DEV] Compute retrieval accuracy and visualize results.

    Args:
      res_dir: directory to put result data.
    """
    # get result display name from save directory.
    res_name = self.res_dir.rstrip("/")
    res_name = os.path.basename(res_name)
    self.logger.info("start evaluation...")
    # compute accuracy: top1, top5, top10, top20.
    accu_rank = [1, 5, 10, 20]
    top_k_accu = [0, 0, 0, 0]
    # for each query.
    for query_id, cur_ranked_ids in enumerate(self.ranked_lists):
      for k, rank in enumerate(accu_rank):
        top_k_accu[k] += np.mean([
            1
            if self.query_items[query_id]["label"] == self.db_items[x]["label"]
            else 0 for x in cur_ranked_ids[:rank]
        ])
    top_k_accu = [x / len(self.query_items) for x in top_k_accu]
    # visualize results.
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    j2_env = Environment(loader=FileSystemLoader(cur_dir), trim_blocks=True)
    # prepare ranked list filenames: [query, db_list].
    db_ranked_fns = []
    db_ranked_labels = []
    for cur_ranked_ids in self.ranked_lists:
      db_ranked_fns.append(
          [self.db_items[x]["img_fn"] for x in cur_ranked_ids[:10]])
      db_ranked_labels.append(
          [self.db_items[x]["label"] for x in cur_ranked_ids[:10]])
    # render webpage.
    query_files = [x["img_fn"] for x in self.query_items]
    query_labels = [x["label"] for x in self.query_items]
    res_str = j2_env.get_template("match_vis_temp.html").render(
        test_name=res_name,
        query_fns=query_files[:100],
        query_labels=query_labels[:100],
        db_fns=db_ranked_fns[:100],
        db_labels=db_ranked_labels[:100],
        rank_accu=zip(accu_rank, top_k_accu))
    res_fn = os.path.join(self.res_dir, "match_vis.html")
    with open(res_fn, "w") as fn:
      fn.write(res_str)
      self.logger.info("results saved to {}".format(res_fn))

  def run_dev(self,
              img_folder,
              img_exts,
              load_items_from_db=False,
              compute_feats=False,
              compress_feats=False,
              train_compressor=False):
    """[DEV] All in one method to run pipeline.

    Be able to use the same data split with different
    features for comparison.
    """
    if load_items_from_db:
      self.load_items_from_db()
    else:
      self.read_data_from_files(img_folder, img_exts)
      self.load_items_from_db()
    if compute_feats:
      self.compute_feats()
    self.train_feat_compressor = train_compressor
    if compress_feats:
      self.compress_feats()
    self.run_match()
    self.evaluate()

  def start_dev(self,
                feature,
                feat_comp_batch_size=20,
                use_feat_compressor=True,
                compress_feat_dim=128,
                feat_compress_batch_size=200,
                match_protocol=search_common.MatchProtocol.EXACT,
                num_match_trees=100):
    """Set up dev environment.
    """
    # set up feature extractor.
    self.feat_extractor = feature
    self.target_feat_name = feature.feat_name
    self.target_feat_dim = feature.get_feat_dim()
    self.mode = PipelineMode.DEVELOPMENT
    self.feat_compute_batch_size = feat_comp_batch_size
    self.logger.info("starting feature extractor...")
    startt = time.time()
    self.feat_extractor.start()
    self.logger.info("feature extractor started, time: {}s.".format(time.time()
                                                                    - startt))
    # set up feature compressor.
    self.use_feat_compressor = use_feat_compressor
    self.feat_compress_batch_size = feat_compress_batch_size
    self.compress_feat_dim = compress_feat_dim
    if self.use_feat_compressor:
      self.feat_compressor = dim_reductor.IncrementalPCADimReducer(
          self.res_dir,
          self.compress_feat_dim,
          batch_size=self.feat_compress_batch_size)
      self.target_feat_dim = self.compress_feat_dim
    # set up matcher.
    self.match_protocol = match_protocol
    self.num_trees = num_match_trees
    if self.match_protocol == search_common.MatchProtocol.APPROXIMATE:
      self.matcher = simple_matchers.ANNMatcher(
          "{}_matcher".format(self.task_name), search_common.MatcherType.L2,
          self.target_feat_dim, self.num_trees, self.res_dir)
    else:
      self.matcher = simple_matchers.ExactMatcher(
          "{}_matcher".format(self.task_name), search_common.MatcherType.L2,
          self.res_dir)

  def start_deploy(self,
                   feature,
                   use_feat_compressor=True,
                   compress_feat_dim=128,
                   match_protocol=search_common.MatchProtocol.EXACT,
                   num_match_trees=100):
    """Set up and get ready for production.
    """
    # load featur extractor.
    self.feat_extractor = feature
    self.target_feat_name = feature.feat_name
    self.target_feat_dim = feature.get_feat_dim()
    self.mode = PipelineMode.DEPLOYMENT
    self.logger.info("starting feature extractor...")
    startt = time.time()
    self.feat_extractor.start()
    self.logger.info("feature extractor started, time: {}s.".format(time.time()
                                                                    - startt))
    # load feature compressor.
    self.use_feat_compressor = use_feat_compressor
    self.compress_feat_dim = compress_feat_dim
    if self.use_feat_compressor:
      self.logger.info("loading feature compressor...")
      self.feat_compressor = dim_reductor.IncrementalPCADimReducer(
          self.res_dir, self.compress_feat_dim)
      self.feat_compressor.save_load_model(to_save=False)
      self.logger.info("feature compressor loaded.")
      self.target_feat_dim = self.compress_feat_dim
    # load matcher.
    self.logger.info("loading matcher...")
    self.match_protocol = match_protocol
    self.num_trees = num_match_trees
    if self.match_protocol == search_common.MatchProtocol.APPROXIMATE:
      self.matcher = simple_matchers.ANNMatcher(
          "{}_matcher".format(self.task_name), search_common.MatcherType.L2,
          self.target_feat_dim, self.num_trees, self.res_dir)
      self.matcher.load_index()
    else:
      self.matcher = simple_matchers.ExactMatcher(
          "{}_matcher".format(self.task_name), search_common.MatcherType.L2,
          self.res_dir)
      self.load_feats_from_db(not self.use_feat_compressor)
    self.logger.info("matcher loaded.")

  def feat_post_process(self, feat):
    """Post processing feature.

    Override for custom process.

    Args:
      feat: 1D 32b float feature vector.
    Returns:
      post processing feature.
    """
    # reduce feature dimension.
    new_feat = feat
    if self.use_feat_compressor:
      if len(feat.shape) == 1:
        feat = feat.reshape((1, -1))
      new_feat = self.feat_compressor.transform(feat)
      new_feat = normalize(new_feat)
    return new_feat

  def search(self, img_rgb, res_num):
    """deploy purposed search.

    Args:
      img_rgb: input image query.
      res_num: how many results to retrieve.
    Returns:
      result metadata.
    """
    # compute feature.
    feat = self.feat_extractor.compute(img_rgb)
    # pose processing.
    new_feat = self.feat_post_process(feat)
    # search.
    query_items = {"metadata": [], "features": new_feat}
    ranked_list = self.matcher.match(query_items, top_nn=res_num)
    res_data = [self.matcher.db_metadata[x] for x in ranked_list[0]]
    return res_data
