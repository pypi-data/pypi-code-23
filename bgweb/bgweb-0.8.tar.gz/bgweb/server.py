import logging

import cherrypy


class BGServer:
    """
    Server base class. Initializes the cherrypy server and configures it

    Args:
        configuration (dict): server configuration. Must include at least host and port
    """

    def __init__(self, configuration):

        self.conf = configuration

        cherrypy.config.update({'server.socket_port': int(self.conf['port'])})
        cherrypy.config.update({'server.socket_host': self.conf['host']})

        self.configure()

    def configure(self):
        """
        This method is designed to be overwritten by the user
        so they can do modify the configuration
        """
        pass

    def add_app(self, web_app):
        """
        Mounts a web application

        Args:
            web_app (:class:`~bgweb.web.BGWeb`): web application
        """
        logging.getLogger(__name__).debug('Adding app to server on %s using the configuration %s' % (web_app.mount_point, web_app.server_conf))
        cherrypy.tree.mount(web_app, web_app.mount_point, web_app.server_conf)

    def run(self):
        """
        Run the cherrypy server with the application
        """
        cherrypy.engine.start()
        cherrypy.engine.block()
