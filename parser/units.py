# ======================================================================
# >> Imports
# ======================================================================

# Python
from collections import namedtuple

# HttsHots
from . import consts, parse


# ======================================================================
# >> Consts
# ======================================================================
Death = namedtuple('Death', ['gameloop', 'killers'])

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
        self.dead_gameloop = -1
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


class HeroUnit:
    def __init__(self, event):
        self.player_id = event['m_intData'][0]['m_value']
        hero_name = event['m_stringData'][0]['m_value']
        self.hero_name = parse.decode_string(hero_name)

        # gameloop: Death
        self.deaths = []

    def add_death(self, event):
        gameloop = event['_gameloop']
        killers = []
        for info in event['m_intData'][1:]:
            killers.append(info['m_value'])
        self.deaths.append(Death(gameloop, killers))



# ======================================================================
# >> Functions
# ======================================================================
def get_unit_tag(event):
    return (event['m_unitTagIndex'] << 18) + event['m_unitTagRecycle']


def get_hero_unit(event):
    return event['m_intData'][0]['m_value']
