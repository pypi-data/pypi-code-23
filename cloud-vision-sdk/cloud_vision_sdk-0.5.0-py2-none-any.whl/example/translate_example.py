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

credential = Credential(galaxy_access_key="AKLFWE25G7USVQLQX5", galaxy_key_secret="RKQmtJF+JI/pMtnbxie8jGu6rFTwD59r/Vwv9Rki")
vision_client = VisionClient(credential=credential, endpoint="cnbj2.vision.api.xiaomi.com")

#For more supported language and format, please go to http://wiki.n.miui.com/pages/viewpage.action?pageId=63615063
nlp_translation_request = NlpTranslationRequest(fromLanguage="en", toLanguage="zh-chs",text="Hello World")
nlp_translation_result = vision_client.nlp_translation(nlp_translation_request)
print nlp_translation_result.result
