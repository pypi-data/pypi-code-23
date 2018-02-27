# Copyright 2017 Xiaomi, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

# -*- coding: utf-8 -*-

import urlparse
import visionconfig

class Credential:
  def __init__(self, galaxy_access_key=None, galaxy_key_secret=None):
    """
    :param galaxy_access_key: string
    user's access key id
    :param galaxy_key_secret: string
    user's secret access key
    :return : Credential object
    """
    self.galaxy_access_key = galaxy_access_key
    self.galaxy_key_secret = galaxy_key_secret

class Image:
  def __init__(self, uri=None, content=None):
    if uri is not None:
      self.__check_uri(uri)
    self.uri = uri
    if content is not None:
      self.__check_content(content)
    self.content = content

  def __check_uri(self, uri):
    url = urlparse.urlparse(uri)
    if url.scheme != visionconfig.FDS_URI_SCHEME:
      raise Exception("uri scheme %s is not support, only support fds scheme now" % url.scheme)
    if not uri.upper().endswith(".JPG"):
      raise Exception("this image format is not support, only support jpg and png format now")

  def __check_content(self, content):
    if isinstance(content, str):
      if len(content) > visionconfig.MAX_REQUEST_IMAGE_SIZE:
        raise Exception("image length exceeded, max allowed: %d" % visionconfig.MAX_REQUEST_IMAGE_SIZE)
    else:
      raise Exception("content should be a str type variable")

  def set_uri(self, uri):
    self.__check_uri(uri)
    self.uri = uri

  def set_content(self, content):
    self.__check_content(content)
    self.content = content


class DetectFacesRequest:
  def __init__(self, image=None):
    self.image = image

  def set_image(self, image):
    self.image = image

class DetectLabelsParam:
  def __init__(self, max_labels=None, min_confidence=None):
    self.maxLabels = max_labels
    self.minConfidence = min_confidence

class DetectLabelsRequest:
  def __init__(self, image=None, param=None):
    self.image = image
    self.param = param

  def set_image(self, image):
    self.image = image

  def set_param(self, param):
    self.param = param

class ExternalDetectLabelRequest:
  def __init__(self, image=None, source=None):
    self.image = image
    self.source = source

class ExternalDetectLabelResult:
  def __init__(self, labels=None):
    self.labels = labels

class FaceCompareRequest:
  def __init__(self, image1=None, image2=None, threshold=None):
    self.firstImage = image1
    self.secondImage = image2
    self.matchThreshold = threshold

  def set_first_image(self, image):
    self.firstImage = image

  def set_second_image(self, image):
    self.secondImage = image

class AgeInfo:
  def __init__(self, age=None, confidence=None):
    self.age = age
    self.confidence = confidence

class GenderInfo:
  def __init__(self, gender=None, confidence=None):
    self.gender = gender
    self.confidence = confidence

class FacePosition:
  def __init__(self, face_x=None, face_y=None, face_h=None, face_w=None,
               eye_left_x=None, eye_left_y=None, eye_right_x=None, eye_right_y=None,
               nose_x=None, nose_y=None, mouth_left_x=None, mouth_left_y=None,
               mouth_right_x=None, mouth_right_y=None):
    self.faceX = face_x
    self.faceY = face_y
    self.faceH = face_h
    self.faceW = face_w
    self.eyeLeftX = eye_left_x
    self.eyeLeftY = eye_left_y
    self.eyeRightX = eye_right_x
    self.eyeRightY = eye_right_y
    self.noseX = nose_x
    self.noseY = nose_y
    self.mouthLeftX = mouth_left_x
    self.mouthLeftY = mouth_left_y
    self.mouthRightX = mouth_right_x
    self.mouthRightY = mouth_right_y

class FaceInfo:
  def __init__(self, face_pos=None, age_info=None, gender_info=None):
    self.facePos = face_pos
    self.ageInfo = age_info
    self.genderInfo = gender_info


class DetectFacesResult:
  def __init__(self, face_info=None):
    self.faceInfo = face_info


class Label:
  def __init__(self, confidence=None, name=None):
    self.confidence = confidence
    self.name = name


class DetectLabelsResult:
  def __init__(self, labels=None):
    self.labels = labels

class FaceMatchResult:
  def __init__(self, is_match=None, score=None):
    self.isMatch = is_match
    self.score = score

class NlpTranslationRequest:
  def __init__(self, fromLanguage=None, toLanguage=None, text=None):
    self.fromLanguage = fromLanguage
    self.toLanguage = toLanguage
    self.text = text

class NlpTranslationResult:
  def __init__(self, status=None, result=None):
    self.status = status
    self.result = result

class OcrLine:
  def __init__(self, boundingBox=None, text=None):
    self.boundingBox = boundingBox
    self.text = text

class OcrTranslateLine:
  def __init__(self, boundingBox=None, text=None, toText=None):
    self.boundingBox = boundingBox
    self.text = text
    self.toText = toText

class OcrRegion:
  def __init__(self, boundingBox=None, lines=None):
    self.boundingBox = boundingBox
    self.lines = lines

class OcrResult:
  def __init__(self, regions=None, status=None, textAngle=None, orientation=None, language=None):
    self.regions = regions
    self.status = status
    self.textAngle = textAngle
    self.orientation = orientation
    self.language = language

class OcrRequest:
  def __init__(self, image=None, language=None):
    self.image = image
    self.language = language

class OcrTranslateRequest:
  def __init__(self, image=None, language=None, to=None):
    self.image = image
    self.language = language
    self.to = to

class OcrTranslateResult:
  def __init__(self, regions=None, status=None, textAngle=None, orientation=None, language=None, to=None):
    self.regions = regions
    self.status = status
    self.textAngle = textAngle
    self.orientation = orientation
    self.language = language
    self.to = to

class VisionException(Exception):
  def __init__(self, errorCode=None, errMsg=None, details=None, requestID=None):
    self.errorCode = errorCode
    self.errMsg = errMsg
    self.details = details
    self.requestId = requestID

  def __str__(self):
    return repr(self)

  def __repr__(self):
    L = ['%s=%r' % (key, value) for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))
