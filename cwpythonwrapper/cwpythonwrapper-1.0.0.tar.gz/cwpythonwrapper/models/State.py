from . import Bot, Bullet, Pod, Powerup, Map


class State:

    def __init__(self, bots: [Bot] = None, bullets: [Bullet] = None, powerups: [Powerup] = None, pods: [Pod] = None,
                 startedOn=None, mapId=None, lastTick=None,
                 lastTickDuration=None, paused=None, map: Map = None):
        self.map = map
        self.paused = paused
        self.lastTickDuration = lastTickDuration
        self.lastTick = lastTick
        self.mapId = mapId
        self.startedOn = startedOn
        self.pods = pods
        self.powerups = powerups
        self.bullets = bullets
        self.bots = bots

    @classmethod
    def fromState(self, state):
        return self(state.bots, state.bullets, state.powerups, state.pods, state.startedOn, state.mapId, state.lastTick,
                    state.lastTickDuration, state.paused, state.map)
