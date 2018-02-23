"""Web api classes.
"""

from flask import request, jsonify

from owl.data.img_obj import OwlImage
from owl.services import web_api
from owl.processors.recognition import common


class ImgClassifierWebAPI(web_api.WebAPIBase):
  """Generic web api for image classification.
  """
  classifier = None

  def __init__(self, api_name, clf_obj):
    """Initialize api.
    """
    super(ImgClassifierWebAPI, self).__init__(api_name)
    assert isinstance(clf_obj, common.ImgClassifierBase)
    self.classifier = clf_obj
    # add resource.
    self.add_resource("/predict", ["GET", "POST"], self.predict)

  def prepare(self):
    self.classifier.prepare()
    self.started = True

  def parse_clf_request(self, req_json):
    assert "img_base64" in req_json
    return req_json["img_base64"]

  def predict(self):
    """Perform prediction on request image.
    """
    try:
      if request.method == "GET":
        if self.started:
          return "classification service is on"
        else:
          return "classification service is not on"
      if request.method == "POST":
        req_data = request.get_json()
        img_base64 = self.parse_clf_request(req_data)
        img_obj = OwlImage(img_base64=img_base64)
        clf_pred = self.classifier.predict(img_obj)
        res_obj = web_api.make_success_res_obj(clf_pred.to_json())
        print res_obj
        return jsonify(res_obj), 200
    except Exception as ex:
      print "[{}] {}".format(self.__class__.__name__, ex)
      return jsonify(web_api.make_error_res_obj(ex.message)), 500

  def update_predict_path(self, new_path):
    """Change default predict url path.
    """
    # TODO(jiefeng): figure out how to remove the existing one.
    self.add_resource(new_path, ["GET", "POST"], self.predict)


class ImgDetectorWebAPI(web_api.WebAPIBase):
  """Generic web api for image detection.
  """
  detector = None

  def __init__(self, api_name, detector_obj):
    """Initialize api.
    """
    super(ImgDetectorWebAPI, self).__init__(api_name)
    assert isinstance(clf_obj, common.ImgDetectorBase)
    self.detector = detector_obj
    # add resource.
    self.add_resource("/predict", ["GET", "POST"], self.predict)

  def prepare(self):
    self.detector.prepare()
    self.started = True

  def predict(self):
    """Perform prediction on request image.
    """
    try:
      if request.method == "GET":
        if self.started:
          return "detection service is on"
        else:
          return "detection service is not on"
      if request.method == "POST":
        req_data = request.get_json()
        pass

    except Exception as ex:
      return jsonify(web_api.make_error_res_obj(ex.message)), 500

  def update_predict_path(self, new_path):
    """Change default predict url path.
    """
    self.add_resource(new_path, ["GET", "POST"], self.predict)