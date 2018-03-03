"""Clarifai api manager.

Need to create account and obtain api key.
"""

import json

from clarifai import rest
from clarifai.rest import ClarifaiApp


class ClarifaiAPI(object):
  """Class to manage clarifai api.
  """
  client = None

  def __init__(self, api_key):
    self.client = ClarifaiApp(api_key=api_key)

  def label_img_general(self,
                        img_url=None,
                        img_base64=None,
                        img_bin=None,
                        img_fn=None,
                        top_k=10):
    """Predict image labels using general model.
    
    Use any non-empty value as image.
    """
    model = self.client.models.get("general-v1.3")
    if img_url is not None:
      res = model.predict_by_url(img_url, max_concepts=top_k)
    if img_base64 is not None:
      res = model.predict_by_base64(img_base64, max_concepts=top_k)
    if img_bin is not None:
      res = model.predict_by_bytes(img_bin, max_concepts=top_k)
    if img_fn is not None:
      res = model.predict_by_filename(img_fn, max_concepts=top_k)
    new_res = []
    for item in res["outputs"][0]["data"]["concepts"]:
      new_res.append((item["name"], item["value"]))
    return new_res
