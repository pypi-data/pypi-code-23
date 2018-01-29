from flask.json import JSONEncoder
import zope.event
import inject
from flask import Flask
import datetime
import threading
import applauncher.kernel
from flask_cors import CORS
from applauncher.kernel import Environments, Kernel


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return JSONEncoder.default(self, obj)


# Just for inject an array as ApiBlueprints
class ApiBlueprints(object):
    pass


class FlaskBundle(object):
    app = None
    def __init__(self):
        self.config_mapping = {
            "flask": {
                "use_debugger": False,
                "port": 3003,
                "host": "0.0.0.0",
                "cors": False,
                "debug": False,
                "secret_key": "cHanGeME"
            }
        }

        self.blueprints = []
        self.injection_bindings = {
            ApiBlueprints: self.blueprints
        }

        zope.event.subscribers.append(self.kernel_ready)

    @inject.params(config=applauncher.kernel.Configuration)
    def start_sever(self, config):
        app = Flask("FlaskServer")

        app.json_encoder = CustomJSONEncoder

        for blueprint in self.blueprints:
            app.register_blueprint(blueprint)

        c = config.flask
        app.secret_key = c.secret_key
        FlaskBundle.app = app
        if c.cors:
            CORS(app)

        if c.debug:
            kernel = inject.instance(Kernel)
            if kernel.environment != Environments.TEST:
                app.run(use_debugger=c.use_debugger, port=c.port, host=c.host)


    def kernel_ready(self, event):
        if isinstance(event, applauncher.kernel.KernelReadyEvent):
            kernel = inject.instance(applauncher.kernel.Kernel)
            c = inject.instance(applauncher.kernel.Configuration).flask
            if c.debug:
                t = threading.Thread(target=self.start_sever)
                t.start()
            else:
                self.start_sever()


