from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
#from flask_restplus import Api
import logging
from logging.handlers import RotatingFileHandler
from logging import FileHandler
import os
from os.path import expanduser
import yaml
#from cloghandler import ConcurrentRotatingFileHandler

from flask_zipkin import Zipkin

#zipkin = Zipkin(sample_rate=10)


from .config import config_by_name
import sys

toolbar = DebugToolbarExtension()

#api = Api()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    
    #init debug toolbar
    toolbar.init_app(app)
    #init api restplus
    #api.init_app(app)

    #zipkin.init_app(app)

    from inol_rest.home import home as home_blueprint
    app.register_blueprint(home_blueprint, url_prefix='/')

    from inol_rest.api import api_blueprint as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    #setup logging
    
    if os.getenv("INOL_REST_DEBUG", None) is not None:
        __setup_logging(default_level=logging.DEBUG)
    else:
        __setup_logging()
    
    #handler = FileHandler('C:/var/tmp/flask.log', mode='w')
    #handler.setLevel(logging.INFO)
    #app.logger.addHandler(handler)


    return app


 
def __setup_logging(default_level=logging.FATAL):
    """
    Setup logging configuration
    #https://docs.python.org/2/library/logging.config.html#logging-config-dictschema
    """
    #print default_level
    default_format = "%(asctime)s - %(levelname)s - %(name)s - %(module)s.%(funcName)s: %(message)s"
    
    home_dir = expanduser("~")
    
    logging_config = os.getenv("INOL_REST_LOG_YAML", '{0}/logging.yaml'.format(home_dir))
    
    
    if os.path.exists(logging_config):
        #try as if logging_config is an absolute path
        with open(logging_config, 'rt') as f:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)
    else:
        #print "WARN: could not find {0}".format(logging_config)
        #log to stderr. This works better with ansible
        logging.basicConfig(level=default_level, format=default_format,stream=sys.stderr)
        
    logger = logging.getLogger( __name__ )
    logger.debug("logging init complete")