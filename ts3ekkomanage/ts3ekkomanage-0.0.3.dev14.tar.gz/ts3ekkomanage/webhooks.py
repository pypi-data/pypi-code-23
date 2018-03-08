import bottle
import threading
import logging

class EkkoReverseClientContact:
    def __init__(self, ekkomanager, web_port=8180):
        self._app = bottle.Bottle()
        self._ekkomanager = ekkomanager
        self._routes()
        self._thread = threading.Thread(target=self._app.run, kwargs=dict(host='0.0.0.0', port=int(web_port)))

    def _routes(self):
        """
        Set up web API routes.
        :return:
        """
        self._app.route('/cmd/spawn/<channel_id>', callback=self.spawn)
        self._app.route('/cmd/spawn/<channel_id>/<channel_password>', callback=self.spawn)
        self._app.route('/cmd/despawn/<ekko_node_id>', callback=self.despawn)

    def spawn(self, channel_id, channel_password=None):
        """
        Relay client spawn from api to manager.
        :param channel_id: TeamSpeak3 cid.
        :param channel_password: password of the channel (optional)
        """
        self._ekkomanager.spawn(channel_id, channel_password)

    def despawn(self, ekko_node_id):
        logging.debug(f'DESPAWN WEBHOOK: {ekko_node_id}')
        self._ekkomanager.despawn(ekko_node_id)

    def start(self):
        self._thread.start()
