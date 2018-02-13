
COOKIE_MAX_AGE = 3600 * 24 * 120


class BGWeb:
    """
    Web application base class

    Args:
        configuration (dict): dictionary with the configuration of this web application
        static_dirs (dict): dictionary with the static content

    The configuration dict:
    - It must contain, at least, the mount point for the app. E.g. {'mount_point' : '/'}.
    - The optional key 'server_conf' will be used to configure the application in cherrypy.
       If the key is provided, its value must be a dict.
    """

    def __init__(self, configuration, static_dirs={}):

        self.mount_point = configuration['mount_point']
        # Sessions and authentication tools should be enalbed in the root '/'
        self.server_conf = {'/': {}}
        self.server_conf.update(configuration.get('server_conf', {}))

        self._add_static(static_dirs)

    def _add_static(self, static_dirs):
        """
        Add static content to the server configuration

        Args:
            static_dirs (dict): directories with the static content

        """
        for static_dir, value in static_dirs.items():
            if type(value) == dict:
                self.server_conf[static_dir] = value
            elif type(value) == str:
                self.server_conf[static_dir] = {
                    'tools.staticdir.on': True,
                    'tools.staticdir.dir': value
                }
