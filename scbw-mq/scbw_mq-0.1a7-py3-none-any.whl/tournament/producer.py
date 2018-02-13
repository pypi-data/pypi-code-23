import logging
import os
from argparse import Namespace
from random import choice

import pika
from pika import PlainCredentials
from scbw.bot_factory import retrieve_bots
from scbw.bot_storage import LocalBotStorage, SscaitBotStorage
from scbw.map import download_sscait_maps, check_map_exists

from .message import PlayMessage
from .utils import read_lines

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
        n = 0

        repeat = [545, 1423, 1590, 1591, 1592, 1598, 2040, 2162, 2347, 2498, 2596, 2755, 2975, 3142,
                  3165, 3173, 3176, 3178, 3317, 3323, 3647, 3666, 3672, 3674, 3675, 3679, 3680,
                  4333, 4437, 5001, 5072, 5120, 5725, 5762, 6482, 6675, 6681, 6682, 7123, 7162,
                  1323, 1595, 2159, 2500, 2984, 3168, 3174, 3179, 3662, 3663, 3665, 3673, 3676,
                  4367, 4432, 5746, 6437, 6487, 6678, 7144, 7335, 7742, 7803, 8365, 8387, 9010,
                  9588, 9939, 10006, 10022, 10034, 10103, 10154, 10172, 10194, 10230, 10243, 10323,
                  10330, 10695, 10872, 10876, 11297, 12298, 12893, 12922, 14299, 14618, 14762,
                  14765, 14775, 14823, 14833, 14935, 15617, 16368, 16374, 16462, 17640, 17821,
                  18137, 18208, 18722, 18992, 19234, 19243, 19297, 19347, 19537, 19620, 19712,
                  19945, 20127, 20510, 20537, 20640, 20642, 20653, 20681, 20747, 20800, 20995,
                  20949, 21007, 20991, 21006, 21009, 570, 1331, 1407, 1593, 1601, 2179, 2209, 2319,
                  2501, 3245, 3682, 3688, 3689, 6688, 7705, 8296, 10155, 10236, 10324, 10327, 10757,
                  11667, 11821, 11834, 13254, 13675, 13802, 13896, 13915, 14295, 14312, 14363,
                  14777, 14786, 14812, 16022, 17147, 17192, 17542, 17822, 18127, 18482, 18772,
                  19490, 19549, 20117, 20336, 20472, 20651, 20685, 20686, 20794, 20934, 20975,
                  20962, 20946, 21020, 21039, 21105, 1399, 1602, 1731, 2207, 3113, 3280, 3669, 3671,
                  3677, 4322, 5343, 9634, 9891, 10024, 11837, 13250, 13352, 13355, 13873, 13894,
                  14779, 14785, 14807, 15152, 15579, 15612, 16069, 16745, 17546, 17573, 18184,
                  18390, 19039, 19247, 19316, 19593, 19942, 20520, 20549, 20567, 20601, 20652,
                  20765, 21027, 21038, 21045, 1397, 1594, 1599, 1604, 2017, 2229, 2502, 3171, 3175,
                  3684, 3687, 5345, 6679, 6684, 7097, 7812, 9842, 9869, 10166, 10255, 10334, 10709,
                  11252, 13907, 14379, 14763, 14780, 14783, 14820, 14834, 15606, 16412, 17872,
                  18437, 18793, 19645, 20297, 20347, 20452, 20508, 20522, 20552, 21035, 20999,
                  21023, 617, 1386, 1603, 1647, 2606, 2897, 2912, 3167, 3169, 3170, 3660, 3661,
                  3685, 5032, 5341, 6685, 7424, 7766, 7805, 8999, 9032, 9405, 9830, 9866, 10009,
                  10029, 10156, 10196, 10206, 10261, 10787, 13353, 14028, 14617, 14770, 14778,
                  14788, 14830, 15132, 15183, 15683, 17491, 17783, 18198, 18736, 18747, 19042,
                  19240, 19292, 19487, 19559, 19629, 19757, 19922, 20125, 20384, 20582, 20597,
                  20658, 20671, 20679, 20931, 986, 2503, 2602, 3166, 3172, 3382, 3668, 3678, 3681,
                  4423, 5351, 6687, 7725, 8363, 8372, 8987, 9587, 9599, 9632, 10171, 10232, 11801,
                  12872, 13912, 14020, 14615, 14776, 14787, 14832, 14849, 15197, 16459, 16787,
                  17839, 18202, 18484, 18487, 18749, 19031, 19474, 19473, 19554, 20042, 20355,
                  20405, 20477, 20492, 20505, 20612, 21024, 21117, 1405, 1444, 1596, 1597, 1600,
                  1718, 2230, 2288, 2234, 2494, 3177, 3664, 3667, 3670, 3683, 3686, 4188, 4651,
                  6461, 6689, 7167, 7748, 8947, 8993, 9574, 9582, 9944, 10011, 10033, 10146, 10167,
                  10223, 10225, 10233, 10339, 10708, 10742, 11342, 12362, 12921, 13367, 13847,
                  13905, 13910, 14622, 14766, 14772, 15981, 16042, 16336, 17451, 17492, 17501,
                  18737, 18784, 19471, 20096, 20327, 20344, 20517, 20523, 20627, 20641, 20650,
                  20659, 20691, 20936, 20959, ]
        for i, bot_a in enumerate(bots):
            for bot_b in bots[(i + 1):]:
                for map_name in maps:
                    game_name = "".join(choice("0123456789ABCDEF") for _ in range(8)) + "_%06d" % n

                    msg = PlayMessage([bot_a, bot_b], map_name, game_name).serialize()
                    n += 1
                    if n in repeat:
                        channel.basic_publish(exchange='', routing_key='play', body=msg)
        logger.info(f"published {n} messages")

    finally:
        connection.close()
