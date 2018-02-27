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

credential = Credential(galaxy_access_key="Your_AK", galaxy_key_secret="Your_SK")
vision_client = VisionClient(credential=credential, endpoint="demo-cloud-vision.api.xiaomi.com")

with open("SAMPLE_IMAGE", "rb") as data:
    content = data.read()
    image = Image(content=content)
external_request = ExternalDetectLabelRequest(image=image, source="EXTERNAL_SOURCE")
external_result = vision_client.external_detect_labels(external_request)
print json.dumps(external_result,ensure_ascii=False, skipkeys=True, default=lambda o: o.__dict__)
