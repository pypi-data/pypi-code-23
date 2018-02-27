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

from cloud_vision.models import *
from cloud_vision.visionclient import Credential, VisionClient
import json
import base64

credential = Credential(galaxy_access_key="Your_AK", galaxy_key_secret="Your_SK")
vision_client = VisionClient(credential=credential, endpoint="cnbj2.vision.api.xiaomi.com")

with open("SAMPLE_IMAGE.jpg", "rb") as data:
    content = data.read()
    image = Image(content=content)
ocr_translation_request = OcrTranslateRequest(image=image, language="en", to="zh-chs")
ocr_translation_result = vision_client.ocr_image_translation(ocr_translation_request)
print json.dumps(ocr_translation_result,ensure_ascii=False, skipkeys=True, default=lambda o: o.__dict__)
