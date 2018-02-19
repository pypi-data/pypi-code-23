import logging
from argparse import Namespace
from typing import Dict

from scbw import DockerException, GameException

from .consumer import JsonConsumer, consumer_error
from .responses import argument_logger

logger = logging.getLogger(__name__)


class PlayConfig(Namespace):
    # rabbit connection
    host: str
    port: int
    user: str
    password: str

    # parallelization
    n_processes: int

    # game settings
    game_type: str
    game_speed: int
    timeout: int
    bot_dir: str
    log_dir: str
    map_dir: str
    bwapi_data_bwta_dir: str
    bwapi_data_bwta2_dir: str
    read_overwrite: bool
    docker_image: str
    opt: str


class PlayConsumer(JsonConsumer):
    EXCHANGE = 'play'
    EXCHANGE_TYPE = 'direct'
    QUEUE = 'play'
    ROUTING_KEY = 'play'

    def __init__(self, config: PlayConfig):
        url = f'amqp://{config.user}:{config.password}@{config.host}:{config.port}/%2F'
        super(PlayConsumer, self).__init__(url)

        self.config = config

    @consumer_error(GameException, DockerException)
    @argument_logger
    def handle_message(self, json_request: Dict):
        logger.info(json_request)
