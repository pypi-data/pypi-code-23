import docker
import docker.types
import asyncio
import logging

from ts3ekkoutil.envconsts import EkkoPropertyNames as epn
from ts3ekkoutil.helpers import help_docker_name

from sqlalchemy_seed import load_fixtures, load_fixture_files
from sqlalchemy.exc import IntegrityError

try:
    from ts3ekkomanage.webhooks import EkkoReverseClientContact
    from ts3ekkomanage.model import Identity, startup
except ImportError:
    from .webhooks import EkkoReverseClientContact
    from .model import Identity, startup


class EkkoNoIdentityAvailable(Exception):
    def __str__(self):
        return "There is no unused identity avilable."


class TS3EkkoManage:
    def __init__(self, args, loop=None, seed_data=True, spawn_first_client=True):
        """
        :param args: configuration dictionary
        :param loop: async event loop
        :param seed_data: if data should be seeded or not
        :param spawn_first_client: if an initial/first client should be spawned on launch
        """
        self.args = args
        self.loop = loop or asyncio.get_event_loop()
        self.reverse_client_contact = EkkoReverseClientContact(self)
        self.docker_conn = docker.from_env()
        self.dbsession = startup(args[epn.DB_USERNAME], args[epn.DB_PASSWORD], args[epn.DB_HOST], args[epn.DB_DBNAME])

        self.clients = []

        if seed_data:
            self.seed_fixtures()

        if spawn_first_client:
            self.spawn()

    @staticmethod
    def docker_ekko_client_prefix(args):
        """
        Defines the naming pattern by which the manager detects client container.
        :param args: configuration dictionary including all possible options to choose from.
        :return: prefix of all client container names
        """
        return args[epn.TS3_USERNAME]

    def spawn(self, channel_id=0, channel_password=None, spawn_invoke_event=None):
        """
        Spawn a new ekko client node. Includes finding an available identity.
        :param channel_id: Id of the channel the client should connect to.
        :param channel_password: Password of the channel (optional)
        :param spawn_invoke_event: identifier if spawn is invoked by user through command/event or through manager init.
        """
        logging.info(f'current existing clients: {self.clients}')

        try:
            # Start of by checking if we still have identites left and find an unused one
            new_identity = self.find_unused_identity()

            # Start preparing the configuration of the new container by copying the base config.
            new_client = self.args.copy()
            new_client[epn.EKKO_NODE_ID] = self.find_unused_node_id()
            new_client[epn.TS3_CHANNEL_ID] = channel_id
            # WARNING: dont remove the prefix, otherwise containers wont get cleared up on manager restart
            new_client[epn.TS3_USERNAME] = f'{self.docker_ekko_client_prefix(new_client)} ' \
                                           f'{new_client[epn.EKKO_NODE_ID]}'
            new_client[epn.TS3_UNIQUE_ID] = new_identity.unique_ts3_id
            new_client[epn.TS3_IDENTITY] = new_identity.private_identity
            new_client[epn.TS3_CHANNEL_PASSWORD] = channel_password

            # Mount the media directoy into the container so that the client can access local media files.
            media_mount = docker.types.Mount(new_client[epn.EKKO_MEDIA_DIRECTORY],
                                             new_client[epn.EKKO_MEDIA_DIRECTORY_SOURCE], read_only=True,
                                             type='bind')

            # Create & run the container with the prepared configuration.
            self.docker_conn.containers.run(image=self.args[epn.DOCKER_EKKO_CLIENT_IMAGE_NAME], detach=True,
                                            name=help_docker_name(new_client[epn.TS3_USERNAME]),
                                            environment=new_client,
                                            auto_remove=not self.args[epn.DOCKER_DISABLE_AUTOREMOVE],
                                            network=self.args[epn.DOCKER_NETWORK_NAME],
                                            links=[new_client[epn.DOCKER_NETWORK_DBLINK].split(':', maxsplit=1)],
                                            mounts=[media_mount])

            # Put the client into the list of running clients.
            self.clients.append(new_client)
            logging.info(f'spawned new client instance: {new_client[epn.TS3_USERNAME]} // '
                         f'{new_client[epn.EKKO_NODE_ID]}')
        except EkkoNoIdentityAvailable as e:
            # TODO: add response to invoker
            # requires addition to webapi to make responses to client requests
            logging.warning(e)
            if spawn_invoke_event is not None:
                pass
            print(e)

    def despawn(self, ekko_node_id: int):
        """
        Despawn the ts3ekko client with the given node id. 
        Despawning equals container stop and removal in current implementation.
        
        :param ekko_node_id: identification of the node to be despawned
        """
        for client in self.clients:
            logging.debug(f'probing client for despawn: {client[epn.TS3_USERNAME]}')
            if str(ekko_node_id) == str(client[epn.EKKO_NODE_ID]):
                try:
                    logging.debug(f'despawning container: {help_docker_name(client[epn.TS3_USERNAME])}')
                    self.docker_conn.containers.get(help_docker_name(client[epn.TS3_USERNAME])).stop()
                    self.clients.remove(client)
                except Exception as e:
                    logging.critical(e)

    def find_unused_identity(self) -> Identity:
        """
        Query the database for ts3 identities. Compare with currently used identities in the client repository and return the first unused one.
        :return unused identity: Identity
        :raises EkkoNoIdentityAvailable: if no unused identity can be found
        """
        all_identities = self.dbsession.query(Identity)
        used_identities = [client[epn.TS3_IDENTITY] for client in self.clients]
        unused_identities = [ident for ident in all_identities if ident.private_identity not in used_identities]
        if unused_identities:
            return unused_identities[0]
        else:
            raise EkkoNoIdentityAvailable()

    def find_unused_node_id(self) -> int:
        """
        Generate a new, unused node identification.
        :return: new, unused node id (int)
        """
        node_id_list = sorted([client[epn.EKKO_NODE_ID] for client in self.clients])
        if node_id_list:
            return node_id_list[-1] + 1
        else:
            return 1

    def seed_fixtures(self):
        """
        Initialise data in database based on the seed files:
        
          - identities.yaml
          - permission.yaml
          - permission_doc.yaml
        
        The data is loaded per file. If any content of the file raises an integrity error, 
        the whole file data gets discarded and not seeded.
        """
        try:
            fixtures = load_fixture_files(self.args[epn.EKKO_FIXTURES_PATH], ['identities.yaml'])
            load_fixtures(self.dbsession, fixtures)
        except IntegrityError:
            logging.info('Identity-fixtures already initialised')

        try:
            fixtures = load_fixture_files(self.args[epn.EKKO_FIXTURES_PATH], ['permission.yaml'])
            load_fixtures(self.dbsession, fixtures)
        except IntegrityError:
            logging.info('Permission-fixtures already initialised')

        try:
            fixtures = load_fixture_files(self.args[epn.EKKO_FIXTURES_PATH], ['permission_doc.yaml'])
            load_fixtures(self.dbsession, fixtures)
        except IntegrityError:
            logging.info('Permission_doc-fixtures already initialised')

    async def periodic_update(self, delay=10):
        while True:
            await asyncio.sleep(delay)

    def start(self):
        self.reverse_client_contact.start()
        self.loop.run_until_complete(
            asyncio.wait([
                self.periodic_update(),
            ])
        )
