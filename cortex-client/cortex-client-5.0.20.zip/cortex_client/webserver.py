"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import json

from flask import Flask
from flask import request

from .types import mk_inputMessage

webserver_app = Flask(__name__)

@webserver_app.route("/health")
def hello():
    return "OK!"

@webserver_app.route("/inquire", methods=['POST'])
def inquire():
    print("Got: {}".format(request.json))
    input_msg = mk_inputMessage(request.json)
    result = webserver_app.modelrunner.run_inquire(input_msg)
    try: 
        return json.dumps(result)
    except TypeError:
        return str(result)

if __name__ == "__main__":
    webserver_app.run(host='0.0.0.0', debug=True, port=9091, use_reloader=False)
