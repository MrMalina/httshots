# ======================================================================
# >> Imports
# ======================================================================

# HttsHots
from . import consts, parse


# ======================================================================
# >> Classes
# ======================================================================
class GameUnit:
    def __init__(self, event):
        # Born
        self.born_gameloop = event['_gameloop']
        self.control_player_id = event['m_controlPlayerId']
        self.index = event['m_unitTagIndex']
        self.name = parse.decode_string(event['m_unitTypeName'])
        self.recycle = event['m_unitTagRecycle']
        self.upkeep_player_id = event['m_upkeepPlayerId']
        self.born_coords = (event['m_x'], event['m_y'])

        # dead
        self.dead_gameloop = None
        self.killer_player_id = None
        self.killer_index = None
        self.killer_recycle = None
        self.dead_coords = None

        # Other
        self.alive_time = -1
        self.tag = self.get_unit_tag()

    def get_unit_tag(self):
        return (self.index << 18) + self.recycle

    def unit_dead(self, event):
        self.dead_gameloop = event['_gameloop']
        self.killer_player_id = event['m_killerPlayerId']
        self.killer_index = event['m_killerUnitTagIndex']
        self.killer_recycle = event['m_killerUnitTagRecycle']
        self.dead_coords = (event['m_x'], event['m_y'])

        self.alive_time = self.dead_gameloop - self.born_gameloop

    def is_meat(self):
        return 'ButcherFreshMeat' in self.name

    def was_picked(self):
        return self.alive_time < consts.ALIVE_TIME[self.name]


# ======================================================================
# >> Functions
# ======================================================================
def get_unit_tag(event):
    return (event['m_unitTagIndex'] << 18) + event['m_unitTagRecycle']
