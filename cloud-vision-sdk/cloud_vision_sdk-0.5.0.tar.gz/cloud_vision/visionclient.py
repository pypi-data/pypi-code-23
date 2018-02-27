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

import copy
import rfc822
import time
import utils
import configs
import json

import httpclient
from models import *

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

class VisionClient:

  FACE_ANALYSIS_RESOURCE = "/api/v1/vision/face-analysis"
  FACE_COMPARISION_RESOURCE = "/api/v1/vision/face-comparison"
  IMAGE_DETECTION_RESOURCE = "/api/v1/vision/image-detection"
  NLP_TRANSLATION_RESOURCE = "/api/v1/translation/text"
  OCR_DETECTION_RESOURCE = "/api/v1/vision/ocr"
  OCR_IMAGE_TRANSLATION_RESOURCE = "/api/v1/translation/image"
  def __init__(self, credential=None, endpoint=None, https_enables=False):
    """
    :param credential: object
      user's credential information
    :param endpoint: string
      the service cluster region user want to use
    :return: VisionClient object
    """
    self.__credential = credential
    self.__endpoint = endpoint
    if ":" in endpoint:
      token = endpoint.strip().split(":")
      self.__host = token[0]
      self.__port = int(token[1])
    else:
      self.__host = endpoint
      self.__port = 80
    self.__uri_prefix = "http://"
    self.__method = "POST"
    if https_enables:
      self.__uri_prefix = "https://"
    self.__face_analysis_uri = self.__uri_prefix + self.__endpoint + VisionClient.FACE_ANALYSIS_RESOURCE
    self.__face_comparision_uri = self.__uri_prefix + self.__endpoint + VisionClient.FACE_COMPARISION_RESOURCE
    self.__image_detection_uri = self.__uri_prefix + self.__endpoint + VisionClient.IMAGE_DETECTION_RESOURCE
    self.__translate_uri = self.__uri_prefix + self.__endpoint + VisionClient.NLP_TRANSLATION_RESOURCE
    self.__ocr_uri = self.__uri_prefix + self.__endpoint + VisionClient.OCR_DETECTION_RESOURCE
    self.__ocr_image_translation_uri = self.__uri_prefix + self.__endpoint + VisionClient.OCR_IMAGE_TRANSLATION_RESOURCE
  def __set_headers(self):
    headers = dict()
    headers[configs.CONTENT_TYPE] = "application/json; charset=UTF-8"
    headers[configs.DATE] = rfc822.formatdate(time.time())
    headers[configs.REQUEST_ID] = utils.request_id()
    headers[configs.CONTENT_MD5] = ""
    return headers

  def __check_parameter(self, image):
    if not isinstance(image,Image):
      raise TypeError("the image parameter of request Object must be Image instance!")
    if image.content is None and image.uri is None:
      raise VisionException(errMsg="the uri and the content of Image object can't all be None")

  def __translate_result2obj(self, response):
    """
    convert a dict to NplTranslateResult
    :param response: dict
      a dict convert by json string
    :return: Object
      NplTranslateResult
    """
    result = None
    if response is None:
      return result
    result = NlpTranslationResult()
    result.status = response["status"]
    result.result = response["result"]
    return result

  def __ocr_result2obj(self, response):
    """
    convert a dict to OcrResult
    :param response: dict
      a dict convert by json string
    :return: Object
      OcrResult
    """
    result = None
    if response is None:
      return result
    result = OcrResult()
    result.status = response["status"]
    result.textAngle = response["textAngle"]
    result.orientation = response["orientation"]
    result.language = response["language"]
    regions = []
    for region in response["regions"]:
      lines = []
      for line in region["lines"]:
        lines.append(OcrLine(boundingBox=line["boundingBox"], text=line["text"]))
      curRegion = OcrRegion(boundingBox=region["boundingBox"],lines=lines)
      regions.append(curRegion)
    result.regions = regions
    return result

  def __ocr_translate_result2obj(self, response):
    """
    convert a dict to OcrTranslateResult
    :param response: dict
      a dict convert by json string
    :return: Object
      OcrTranslateResult
    """
    result = None
    if response is None:
      return result
    result = OcrResult()
    result.status = response["status"]
    result.textAngle = response["textAngle"]
    result.orientation = response["orientation"]
    result.language = response["language"]
    result.to = response["to"]
    regions = []
    for region in response["regions"]:
      lines = []
      for line in region["lines"]:
        lines.append(OcrTranslateLine(boundingBox=line["boundingBox"], text=line["text"], toText=line["toText"]))
      curRegion = OcrRegion(boundingBox=region["boundingBox"],lines=lines)
      regions.append(curRegion)
    result.regions = regions
    return result

  def __match_result2obj(self, response):
    """
    convert a dict to FaceMatchResult
    :param response: dict
      a dict convert by json string
    :return: Object
      FaceMatchResult
    """
    result = None
    if response is None:
      return result
    result = FaceMatchResult()
    result.isMatch = response["isMatch"]
    result.score = response["score"]
    return result

  def __detect_result2obj(self, response):
    """
    convert a dict to DetectFaceResult, DetectLabelsResult
    :param response: dict
      a dict convert by json string
    :return: Object
      such as DetectFaceResult, DetectLabelsResult etc
    """
    result = None
    if response is None:
      return result
    if isinstance(response, dict) and "detectFacesResult" in response and \
            response["detectFacesResult"]:
      result = DetectFacesResult()
      detect_faces_result = response["detectFacesResult"]
      if "faceDetails" in detect_faces_result:
        face_details_list = detect_faces_result["faceDetails"]
        face_details = []
        for x in face_details_list:
          box = x["boundingBox"]
          bounding_box = BoundingBox(left=box["left"], top=box["top"], width=box["width"], height=box['hight'])
          face_detail = FaceDetail(bounding_box, x.get("age", None), x.get("gender", None), x.get("features", None))
          face_details.append(face_detail)
        result.faceDetails = face_details
    if isinstance(response, dict) and "detectLabelsResult" in response and \
            response["detectLabelsResult"]:
      result = DetectLabelsResult()
      detect_labels_result = response["detectLabelsResult"]
      if "labels" in detect_labels_result:
        detect_labels_list = detect_labels_result["labels"]
        labels = []
        for x in detect_labels_list:
          label = Label(confidence=x["confidence"], name=x["name"])
          labels.append(label)
        result.labels = labels
    return result

  def load_image(self, path):
    bytes_source = None
    try:
      image_file = open(path, "r")
      bytes_source = image_file.read()
    except Exception, e:
      print Exception, ":", e
    finally:
      if image_file is not None:
        image_file.close()
    return bytes_source

  def __encode_image(self, image):
    self.__check_parameter(image)
    if image.content is not None:
      image.content = utils.base64_encode(image.content)

  def __result_to_DetectLabelsResult(self, response):
    result = DetectLabelsResult()
    result.labels = []
    for label_data in response["labels"]:
      label = utils.dict2obj(label_data, Label())
      result.labels.append(label)
    return result

  def detect_labels(self, *args, **kwargs):
    """
    # the interface form hasn't been decided, so here use the common form
    :param args:
      args[0]: ImageDetectRequest Object
    :param kwargs: dict
      Temporarily not used, remain
    :return:DetectLabelsResult Object
    """
    if not isinstance(args[0], DetectLabelsRequest):
      raise TypeError("The first argument must be a ImageDetectRequest Object!")
    # here temporary use deepcopy avoid image content be changed
    detect_labels_request = copy.deepcopy(args[0])
    if detect_labels_request is not None \
        and detect_labels_request.image is not None:
      self.__encode_image(detect_labels_request.image)
    params = utils.obj2json(detect_labels_request)
    headers = utils.auth_headers(self.__method, self.__image_detection_uri, self.__set_headers(), self.__credential)
    http_conf = {"method": self.__method, "host": self.__host, "port": self.__port, "resource": self.IMAGE_DETECTION_RESOURCE,
           "timeout": configs.DEFAULT_CLIENT_TIMEOUT}
    response = httpclient.execute_http_request(http_conf, params, headers)
    try:
      if response is None:
        raise VisionException(errMsg="error is occurred, the response is none!")
      return self.__result_to_DetectLabelsResult(response)
    except VisionException, ve:
      print ve
    return None

  def external_detect_labels(self, *args, **kwargs):
    """
    # the interface form hasn't been decided, so here use the common form
    :param args:
      args[0]: ExternalDetectLabelRequest Object
    :param kwargs: dict
      Temporarily not used, remain
    :return:ExternalDetectLabelResult Object
    """
    if not isinstance(args[0], ExternalDetectLabelRequest):
      raise TypeError("The first argument must be a ExternalDetectLabelRequest Object!")
    external_detection_request = copy.deepcopy(args[0])

    external_url = self.__image_detection_uri + "?source=" + external_detection_request.source
    external_resource = VisionClient.IMAGE_DETECTION_RESOURCE + "?source=" + external_detection_request.source
    content = external_detection_request.image.content

    headers = utils.auth_headers(self.__method, external_url, self.__set_headers(), self.__credential)
    http_conf = {"method": self.__method, "host": self.__host, "port": self.__port, "resource": external_resource,
           "timeout": configs.DEFAULT_CLIENT_TIMEOUT}
    response = httpclient.execute_http_request(http_conf, content, headers)
    try:
      result = self.__result_to_DetectLabelsResult(response)
      if result is None:
        raise VisionException(errMsg="error is occurred, the response is none!")
    except VisionException, ve:
      print ve
    return result

  def __result_to_DetectFacesResult(self, response):
    result = DetectFacesResult()
    result.faceInfo = []
    for info_data in response["faceInfo"]:
      info = FaceInfo()
      info.facePos = utils.dict2obj(info_data.get("facePosition", None), FacePosition())
      info.ageInfo = utils.dict2obj(info_data.get("ageInfo", None), AgeInfo())
      info.genderInfo = utils.dict2obj(info_data.get("genderInfo", None), GenderInfo())
      result.faceInfo.append(info)
    return result

  def analysis_faces(self, *args, **kwargs):
    """
    # the interface form hasn't been decided, so here use the common form
    :param args:
      args[0]: ImageDetectRequest Object
    :param kwargs: dict
      Temporarily not used, remain
    :return:DetectFacesResult Object
    """
    if not isinstance(args[0], DetectFacesRequest):
      raise TypeError("The first argument must be a DetectRequest Object!")
    # here temporary use deepcopy avoid image content be changed
    detect_faces_request = copy.deepcopy(args[0])
    # if only uri specified, the content will be None
    if detect_faces_request is not None \
        and detect_faces_request.image is not None:
      self.__encode_image(detect_faces_request.image)
    params = utils.obj2json(detect_faces_request)
    headers = utils.auth_headers(self.__method, self.__face_analysis_uri, self.__set_headers(), self.__credential)
    http_conf = {"method": self.__method, "host": self.__host, "port": self.__port,
           "resource": self.FACE_ANALYSIS_RESOURCE, "timeout": configs.DEFAULT_CLIENT_TIMEOUT}
    response = httpclient.execute_http_request(http_conf, params, headers)
    try:
      if response is None:
        raise VisionException(errMsg="error is occurred, the response is none!")
      return self.__result_to_DetectFacesResult(response)
    except VisionException, ve:
      print ve
    return None

  def match_faces(self, *args, **kwargs):
    """
    # the interface form hasn't been decided, so here use the common form
    :param args:
      args[0]: FaceMatchRequest Object
    :param kwargs: dict
      Temporarily not used, remain
    :return:FaceMatchResult Object
    """
    if not isinstance(args[0], FaceCompareRequest):
      raise TypeError("The first argument must be a FaceMatchRequest Object!")
    face_comparision_request = copy.deepcopy(args[0])
    if face_comparision_request is not None \
        and face_comparision_request.firstImage is not None \
        and face_comparision_request.secondImage is not None:
      self.__encode_image(face_comparision_request.firstImage)
      self.__encode_image(face_comparision_request.secondImage)
    params = utils.obj2json(face_comparision_request)
    headers = utils.auth_headers(self.__method, self.__face_comparision_uri, self.__set_headers(), self.__credential)
    http_conf = {"method": self.__method, "host": self.__host, "port": self.__port, "resource": self.FACE_COMPARISION_RESOURCE,
           "timeout": configs.DEFAULT_CLIENT_TIMEOUT}
    response = httpclient.execute_http_request(http_conf, params, headers)
    result = FaceMatchResult()
    try:
      if response is None:
        raise VisionException(errMsg="error is occurred, the response is none!")
      return utils.dict2obj(response, FaceMatchResult())
    except VisionException, ve:
      print ve
    return result


  def nlp_translation(self, *args, **kwargs):
    """
    # the interface form hasn't been decided, so here use the common form
    :param args:
      args[0]: NlpTranslationRequest Object
    :param kwargs: dict
      Temporarily not used, remain
    :return:NlpTranslationResult Object
    """
    if not isinstance(args[0], NlpTranslationRequest):
      raise TypeError("The first argument must be a NlpTranslationRequest Object!")
    nlp_translation_request = copy.deepcopy(args[0])
    params = json.dumps({"from":nlp_translation_request.fromLanguage, \
             "to":nlp_translation_request.toLanguage, "text":nlp_translation_request.text})

    headers = utils.auth_headers(self.__method, self.__translate_uri, self.__set_headers(), self.__credential)
    http_conf = {"method": self.__method, "host": self.__host, "port": self.__port, "resource": self.NLP_TRANSLATION_RESOURCE,
           "timeout": configs.DEFAULT_CLIENT_TIMEOUT}
    response = httpclient.execute_http_request(http_conf, params, headers)
    try:
      result = self.__translate_result2obj(response)
      if result is None:
        raise VisionException(errMsg="error is occurred, the response is none!")
    except VisionException, ve:
      print ve
    return result

  def ocr_detection(self, *args, **kwargs):
    """
    # the interface form hasn't been decided, so here use the common form
    :param args:
      args[0]: OcrRequest Object
    :param kwargs: dict
      Temporarily not used, remain
    :return:OcrResult Object
    """
    if not isinstance(args[0], OcrRequest):
      raise TypeError("The first argument must be a OcrRequest Object!")
    ocr_detection_request = copy.deepcopy(args[0])
    if ocr_detection_request is not None \
        and ocr_detection_request.image is not None:
      self.__encode_image(ocr_detection_request.image)
    if ocr_detection_request.language == None:
      params = json.dumps({"contentStr":ocr_detection_request.image.content})
    else:
      params = json.dumps({"contentStr":ocr_detection_request.image.content, \
               "language":ocr_detection_request.language})

    headers = utils.auth_headers(self.__method, self.__ocr_uri, self.__set_headers(), self.__credential)
    http_conf = {"method": self.__method, "host": self.__host, "port": self.__port, "resource": self.OCR_DETECTION_RESOURCE,
           "timeout": configs.DEFAULT_CLIENT_TIMEOUT}
    response = httpclient.execute_http_request(http_conf, params, headers)
    try:
      result = self.__ocr_result2obj(response)
      if result is None:
        raise VisionException(errMsg="error is occurred, the response is none!")
    except VisionException, ve:
      print ve
    return result

  def ocr_image_translation(self, *args, **kwargs):
    """
    # the interface form hasn't been decided, so here use the common form
    :param args:
      args[0]: OcrTranslateRequest Object
    :param kwargs: dict
      Temporarily not used, remain
    :return:OcrTranslateResult Object
    """
    if not isinstance(args[0], OcrTranslateRequest):
      raise TypeError("The first argument must be a OcrTranslateRequest Object!")
    ocr_translation_request = copy.deepcopy(args[0])
    if ocr_translation_request.language is None:
      print "Please Provide Source Language!"
      return None
    if ocr_translation_request.to is None:
      print "Please Provide Target Language!"
      return None
    if ocr_translation_request is not None \
        and ocr_translation_request.image is not None:
      self.__encode_image(ocr_translation_request.image)
    params = json.dumps({"contentStr":ocr_translation_request.image.content, \
        "language":ocr_translation_request.language, "to": ocr_translation_request.to})

    headers = utils.auth_headers(self.__method, self.__ocr_image_translation_uri, self.__set_headers(), self.__credential)
    http_conf = {"method": self.__method, "host": self.__host, "port": self.__port, "resource": self.OCR_IMAGE_TRANSLATION_RESOURCE,
           "timeout": configs.DEFAULT_CLIENT_TIMEOUT}
    response = httpclient.execute_http_request(http_conf, params, headers)
    try:
      result = self.__ocr_translate_result2obj(response)
      if result is None:
        raise VisionException(errMsg="error is occurred, the response is none!")
    except VisionException, ve:
      print ve
    return result
