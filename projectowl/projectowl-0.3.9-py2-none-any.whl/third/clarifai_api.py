"""Clarifai api manager.
"""

import json

from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as CImage

client_id = "BtPr5fL-1-9rZzQGYSh2tJsWWzvmPknpa5DSK1YO"
client_secret = "zhXyXyjPdrliHUGfAFmKgNH0XaBDA4j6dtrDHKda"

test_img_url = "https://static1.squarespace.com/static/58b4437f03596e617b3ebd07/58b5c7b8d2b857059b9b705b/58b5c7bdd1758ecc1d4a86ff/1488308168310/eg3.png"


def test():
  app = ClarifaiApp(client_id, client_secret)

  # get the general model
  model = app.models.get("general-v1.3")

  # predict with the model
  preds = model.predict_by_url(url=test_img_url)
  # print json.dumps(preds, sort_keys=True, indent=4, separators=(",", ": "))

  # predict appareal model
  model = app.models.get('apparel')
  image = CImage(url=test_img_url)
  preds = model.predict([image])
  print json.dumps(preds, sort_keys=True, indent=4, separators=(",", ": "))
