import logging
from argparse import Namespace
from random import choice

import os
import pika
from pika import PlainCredentials
from scbw.bot_factory import retrieve_bots
from scbw.bot_storage import LocalBotStorage, SscaitBotStorage
from scbw.map import download_sscait_maps, check_map_exists

from .message import PlayMessage
from ..utils import read_lines

logger = logging.getLogger(__name__)


class ProducerConfig(Namespace):
    # rabbit connection
    host: str
    port: int
    user: str
    password: str

    bot_file: str
    map_file: str
    bot_dir: str
    map_dir: str
    result_dir: str


def launch_producer(args: ProducerConfig):
    bots = read_lines(args.bot_file)
    maps = read_lines(args.map_file)

    # make sure to download bots and maps before producing messages
    bot_storages = (LocalBotStorage(args.bot_dir), SscaitBotStorage(args.bot_dir))
    download_sscait_maps(args.map_dir)
    retrieve_bots(bots, bot_storages)
    for map in maps:
        check_map_exists(args.map_dir + "/" + map)
    os.makedirs(args.result_dir, exist_ok=True)

    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=args.host,
        port=args.port,
        connection_attempts=5,
        retry_delay=3,
        credentials=PlainCredentials(args.user, args.password)
    ))

    try:
        channel = connection.channel()

        logger.info(f"publishing {len(bots)*(len(bots)-1)/2*len(maps)} messages")

        zerg_bots = [
            "AILien",
            "Arrakhammer",
            "Aurelien Lermant",
            "auxanic",
            "Bjorn P Mattsson",
            "Black Crow",
            "Bryan Weber",
            "CasiaBot",
            "CherryPi",
            "Dawid Loranc",
            "ForceBot",
            "HOLD Z",
            "igjbot",
            "KillAlll",
            "Korean",
            "Marian Devecka",
            "Microwave",
            "Neo Edmund Zerg",
            "NLPRbot",
            "PeregrineBot",
            "Pineapple Cactus",
            "Sijia Xu",
            "Steamhammer",
            "UPStarCraftAI 2016",
            "Zia",
            "ZurZurZur",
        ]

        n = 0
        for i, bot_a in enumerate(bots):
            for bot_b in bots[(i + 1):]:
                for map_name in maps:
                    game_name = "".join(choice("0123456789ABCDEF") for _ in range(8)) + "_%06d" % n

                    msg = PlayMessage([bot_a, bot_b], map_name, game_name).serialize()

                    if bot_a == "NUS Bot" or bot_a == "Gaoyuan Chen" \
                            or bot_b == "NUS Bot" or bot_b == "Gaoyuan Chen":
                        pass
                    else:
                        if bot_a in zerg_bots or bot_b in zerg_bots:
                            # print("%06d" % n, bot_a, bot_b, map_name)
                            print("%06d" % n)
                            # channel.basic_publish(exchange='', routing_key='play', body=msg)

                    n += 1
        logger.info(f"published {n} messages")

    finally:
        connection.close()
