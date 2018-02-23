''' cnn features for retrieval
    jiefeng@2016-02-12
'''

import sys
import numpy as np
import time

from common import *

lib_root = 'E:/Projects/Github/deeplearning/Theano/Lasagne/Scripts/'
print 'deep learning folder: ' + lib_root
sys.path.append(lib_root)

from deep_clf import *


class CNNParams(FeatParamsBase):
  feat_type = FeatType.CNN_VGGS
  feat_name = 'cnn_vggs'


class DeepCNNFeature:

  params = CNNParams()

  def __init__(self):
    pass

  def Init(self, cnn_params):
    self.params = cnn_params
    self.config = ExptConfigBase()
    self.config.model_params.img_sz = (224, 224)
    self.config.model_params.output_layer_name = 'output'
    if self.params.feat_type == FeatType.CNN_VGGS or self.params.feat_type == FeatType.CNN_VGGS_SHORT:
      self.model = DeepClfVGGS(self.config.model_params,
                               self.config.train_params)
    if self.params.feat_type == FeatType.CNN_VGG16 or self.params.feat_type == FeatType.CNN_VGG16_SHORT:
      self.model = DeepClfVGG16(self.config.model_params,
                                self.config.train_params)

  def Start(self):
    self.model.build_model()

  def SetInput(self, img_bgr):
    self.img_bgr = img_bgr

  # compute for image
  def Compute(self, mask=None):
    if mask is not None:
      # get bounding box
      locs = cv2.findNonZero(mask)
      box = cv2.boundingRect(locs)
      self.img_bgr = self.img_bgr[box[0]:box[0] + box[2], box[1]:box[1] + box[
          3]]
    self.model.model_params.output_layer_name = 'fc6'
    cnn_input = self.model.prepare_imgs_for_input(np.array([self.img_bgr]))
    feat = self.model.get_outputs(cnn_input)
    feats = np.absolute(feats)
    return feat

  # compute for a set of images
  def ComputeForFns(self, img_fns, mask_fns=None):
    self.model.model_params.output_layer_name = 'fc6'
    cnn_inputs = self.model.prepare_imgfns_for_input(img_fns)
    feats = self.model.get_outputs(cnn_inputs, 10)
    # have to be nonnegative
    feats = np.absolute(feats)
    feats = sklearn.preprocessing.normalize(
        feats, norm='l2', axis=1, copy=False)
    return feats

  def ComputeConvFeats(self, img_fns):
    # conv5_3
    self.model.model_params.output_layer_name = 'conv5'
    cnn_inputs = self.model.prepare_imgfns_for_input(img_fns)
    feats = self.model.get_outputs(cnn_inputs, 10, False)
    # aggregate conv features
    feats = np.sum(feats, axis=(2, 3))
    print feats.shape
    feats = sklearn.preprocessing.normalize(
        feats, norm='l2', axis=1, copy=False)
    return feats
