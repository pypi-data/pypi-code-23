# Benchmarking Suite
# Copyright 2014-2017 Engineering Ingegneria Informatica S.p.A.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Developed in the ARTIST EU project (www.artist-project.eu) and in the
# CloudPerfect EU project (https://cloudperfect.eu/)
import argparse
import logging
import signal
import sys
import json

import os
from flask import Flask
from flask_restplus import Swagger

from benchsuite.rest.apiv1 import blueprint as blueprint1
from benchsuite.rest.apiv1 import api as apiv1
app = Flask(__name__)


#app.config.SWAGGER_UI_JSONEDITOR = True
app.config.SWAGGER_UI_DOC_EXPANSION = 'list'

app.register_blueprint(blueprint1)

def on_exit(sig, func=None):
    print('Bye bye...')
    sys.exit(1)


def dump_swagger_specs():
    app.config['SERVER_NAME'] = 'example.org:80'
    with app.app_context():
        print(json.dumps(Swagger(apiv1).as_dict(), indent=2))


if __name__ == '__main__':

    signal.signal(signal.SIGINT, on_exit)

    logging.basicConfig(
        level=logging.DEBUG,
        stream=sys.stdout)

    parser = argparse.ArgumentParser(prog='benchsuite-rest')
    parser.add_argument('--dump-specs', action='store_true',
                        help='dumps the Swagger specification')
    parser.add_argument('--listen', '-l', type=str,
                        help='set the listening host and port (e.g. 0.0.0.0:80). '
                             'If not specified, the default is 127.0.0.1:5000')


    # parse the arguments. They are taken both from the command line and
    # the BENCHSUITE_REST_OPTS environment variable
    env_opts = os.getenv('BENCHSUITE_REST_OPTS', '').split()
    args = parser.parse_args(sys.argv[1:] + env_opts)



    if args.dump_specs:
        dump_swagger_specs()
        sys.exit(0)



    host = '127.0.0.1'
    port = 5000

    if args.listen:
        if ':' in args.listen:
            t = args.listen.rsplit(':', 1)
            host = t[0]
            port = int(t[1])
        else:
            print('ERROR: wrong format for listening address. '
                  'Must be in the format <host>:<port>')
            sys.exit(1)

    #TODO: use nginx here instead of the internal server
    print('Using internal server. Not use this in production!!!')
    app.run(host=host, port=port, debug=True)

