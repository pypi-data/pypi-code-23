from s2clientprotocol import sc2api_pb2 as sc_pb
from .protocol import Protocol
from .player import Computer

import logging
logger = logging.getLogger(__name__)

class Controller(Protocol):
    def __init__(self, ws):
        super().__init__(ws)

    async def create_game(self, game_map, players, realtime):
        assert isinstance(realtime, bool)
        req = sc_pb.RequestCreateGame(
            local_map=sc_pb.LocalMap(
                map_path=str(game_map.relative_path)
            ),
            realtime=realtime
        )

        for player in players:
            p = req.player_setup.add()
            p.type = player.type.value
            if isinstance(player, Computer):
                p.race = player.race.value
                p.difficulty = player.difficulty.value

        logger.info("Creating new game")
        logger.info(f"Map:     {game_map.name}")
        logger.info(f"Players: {', '.join(str(p) for p in players)}")
        result = await self._execute(create_game=req)
        return result
