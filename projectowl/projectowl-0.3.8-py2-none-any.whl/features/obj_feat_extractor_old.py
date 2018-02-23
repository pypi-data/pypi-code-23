"""Python version of object feature extractor, handles extra features.
   jiefeng @ 2016-02-19
"""

import os
import sys
import commentjson
import cv2
from common import *
from cnn_feats import *

cur_dir = os.path.dirname(os.path.abspath(__file__)) + '/'
engine_root = os.path.join(cur_dir, '../../../')
engine_root = 'E:/Projects/Github/Owl/Owl/'
print engine_root

engine_cpp_lib_path = os.path.join(engine_root, 'CoreEngine/EngineLib/lib/')
sys.path.append(engine_cpp_lib_path)
from EngineLib import ObjFeatExtractorCPP

engine_python_lib_path = os.path.join(engine_root,
                                      'CoreEngine/EngineLibPython/')
sys.path.append(engine_python_lib_path)
from database.DBManager import MongoManager


class UniversalObjFeatExtractor(object):
  """Python interface for feature extraction.

    Universal for c++ and python, should be used for database usage
    usage: init from config file, creat corresponding params and feature extractor
    """

  obj_feat_extractor_cpp = ObjFeatExtractorCPP()
  feat_params = []
  feat_computers = []
  raw_img_bgr = None
  inside_img = None
  config_fn = ''
  extract_cpp = True
  extract_python = True

  # load feature info from json config file
  def Init(self, config_fn):
    self.config_fn = config_fn

    # init cpp part
    self.obj_feat_extractor_cpp.init(config_fn)

    # init python part
    with open(config_fn, 'r') as f:
      config = commentjson.load(f)

    # extract features
    feat_configs = config['engine']['features']
    for feat_config in feat_configs:
      if not feat_config['enabled']:
        continue

      if IsCNNFeat(feat_config['type']):
        # create params
        cur_params = CNNParams()
        cur_params.feat_name = feat_config['type'].encode("utf-8")
        print 'using feature: {}'.format(cur_params.feat_name)
        cur_params.feat_type = MapNameToFeatType(cur_params.feat_name)
        self.feat_params.append(cur_params)
        # create feature
        cnn_feat_computer = DeepCNNFeature()
        cnn_feat_computer.Init(cur_params)
        cnn_feat_computer.Start()
        self.feat_computers.append(cnn_feat_computer)

    print 'feature config loaded'

  def Start(self):
    pass

  # def SetInput(self, img_fn):
  #     self.obj_feat_extractor_cpp.set_input(img_fn)
  #     self.raw_img_bgr = cv2.imread(img_fn)

  # return a dictionary of named features
  def Compute(self, img_fn, mask_fn):
    feats = {}
    # cpp
    if self.extract_cpp:
      feats = self.obj_feat_extractor_cpp.compute(
          img_fn.encode('utf-8'), mask_fn.encode('utf-8'))
    # python
    if self.extract_python:
      for i in range(len(self.feat_params)):
        feat_name = self.feat_params[i].feat_name
        feats[feat_name] = self.feat_computers[i].ComputeForFns(
            [img_fn], [mask_fn]).tolist()[0]

    return feats

  def PopulateDB(self):
    print 'start populating database'

    # connect db
    db_man = MongoManager()
    db_man.load_config(self.config_fn)
    db_man.connect()
    print 'database connected'

    # compute for each item
    total_cnt = db_man.collection.count()
    print 'total object to process: {}'.format(total_cnt)
    valid_num = 0
    cursor = db_man.collection.find()
    for item in cursor:
      try:
        img_fn = item['img_file_path']
        mask_fn = item['mask_file_path']
        cur_feats = self.Compute(img_fn, mask_fn)
        # update each feature
        for feat_name, feat_val in cur_feats.iteritems():
          db_man.update({
              '_id': item['_id']
          }, 'visual_features.' + feat_name, feat_val)
        valid_num += 1
        if valid_num % 1000 == 0:
          print 'finished {}/{}'.format(valid_num, total_cnt)
      except Exception as ex:
        print 'error in {}: {}'.format(img_fn, ex.message)
        continue

    print 'feature extraction done. {}/{} finished. Percentage: {}%'.format(
        valid_num, total_cnt, valid_num * 100.0 / total_cnt)


if __name__ == '__main__':
  config_fn = os.path.join(engine_root,
                           'settings/engine_settings_2016_03.json')
  obj_feat_extractor = UniversalObjFeatExtractor()
  obj_feat_extractor.Init(config_fn)
  obj_feat_extractor.PopulateDB()
