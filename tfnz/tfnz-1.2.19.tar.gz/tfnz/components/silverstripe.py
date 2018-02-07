# Copyright (c) 2018 David Preece, All rights reserved.
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


import logging
from tfnz.location import Location
from tfnz.volume import Volume
from tfnz.endpoint import WebEndpoint, Cluster
from tfnz.components.postgresql import Postgresql


class SilverStripe:
    """An object encapsulating a SilverStripe instance including:
     * load balanced 'server per node'
     * and a Postgresql server"""

    def __init__(self, location: Location, volume: Volume, sql_volume: Volume, fqdn: str, *, log_callback=None):
        """Puts a SilverStripe instance on each node and load balances.

        :param location: A location (object) to connect to.
        :param volume: A volume (object) to use as a persistent store.
        :param sql_volume: A volume to connect to a Postgres server for SQL storage.
        :param fqdn: The FQDN to publish to.
        :param log_callback: An optional callback for log messages -  signature (object, bytes)"""
        # spawn database - logs itself
        self.db = Postgresql(location, sql_volume)

        # spawn one webserver instance on each node
        nodes = location.ranked_nodes()
        self.webservers = [node.spawn_container('tfnz/silverstripe',
                                                volumes=[(volume, '/site')],
                                                sleep=True,
                                                stdout_callback=log_callback) for node in nodes]
        logging.info("Starting SilverStripe servers: " + str([w.uuid.decode() for w in self.webservers]))

        # see if the data volume has been initialised
        try:
            self.webservers[0].fetch("/site/index.php")
        except ValueError as e:
            # need to initialise - /site is visible on all servers
            logging.info("Initialising data volume: " + volume.uuid.decode())
            self.webservers[0].run_process('cp -r /silverstripe/* /site/')

        # recreate the .env because the database ip and password will have changed
        dotenv = SilverStripe.environment_template % (fqdn, self.db.password, self.db.private_ip())
        self.webservers[0].put('/site/.env', dotenv.encode())

        # start the actual webserving process
        fqdn_sed = "sed -i -e 's/--fqdn--/%s/g' /etc/nginx/conf.d/nginx.conf" % fqdn
        timezone_sed = "sed -i -e 's/;date.timezone =/date.timezone = %s/g' /etc/php7/php.ini" % "UTC"  # TODO
        for w in self.webservers:
            self.db.allow_connection_from(w)
            w.run_process(fqdn_sed)
            w.run_process(timezone_sed)
            w.run_process('rm /etc/nginx/conf.d/default.conf')
            w.run_process('mkdir /run/nginx')
            w.spawn_process('nginx', data_callback=log_callback)
            w.spawn_process('php-fpm7', data_callback=log_callback)
            w.spawn_process('tail -f /var/log/nginx/error.log', data_callback=log_callback) \
                if log_callback is not None else None

        # gather together and serve into an endpoint
        self.cluster = Cluster(self.webservers)
        location.endpoint_for(fqdn).publish(self.cluster, fqdn)

        # wait until we're actually able to serve
        WebEndpoint.wait_http_200(fqdn)

        logging.info("SilverStripe is up.")

    environment_template = """
SS_BASE_URL="http://%s"
SS_DATABASE_CLASS="PostgreSQLDatabase"
SS_DATABASE_NAME="SS_mysite"
SS_DATABASE_PASSWORD="%s"
SS_DATABASE_PORT="5432"
SS_DATABASE_SERVER="%s"
SS_DATABASE_USERNAME="postgres"
SS_DEFAULT_ADMIN_USERNAME="admin"
SS_DEFAULT_ADMIN_PASSWORD="password"
"""
