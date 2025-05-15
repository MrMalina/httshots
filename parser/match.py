# ======================================================================
# >> Imports
# ======================================================================

# HttsHots
from . import classes


# ======================================================================
# >> Classes
# ======================================================================
class Game:
    def __init__(self):
        ...

    def add_details(self, data):
        details = classes.Details(data)
        self.details = details
        self.players = details.players

    def add_init_data(self, data):
        self.init_data = classes.InitData(data, self.players)

    def add_header(self, data):
        self.header = classes.Header(data)

    def add_event(self, data):
        classes.TrackerEvents(data, self.players.values())

    def add_lobby(self, data):
        self.lobby = classes.Lobby(data)


class PreGame:
    def __init__(self, bl_players):
        self.players = bl_players

    def get_player_by_index(self, index):
        ret = list(filter(lambda x: x.userid == index, self.players))
        if len(ret):
            return ret[0]
        return None
