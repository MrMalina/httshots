# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
from getpass import getuser

from configobj import ConfigObj
from os import path, sep, listdir

# Httshots
from httshots import parser


# ======================================================================
# >> GLOBAL VARIABLES
# ======================================================================
__version__ = "0.0"

current_user = getuser()
hots_accounts_folder = f"c:\\Users\\{current_user}\\OneDrive\\Documents\\Heroes of the Storm\\Accounts\\"
if not path.isdir(hots_accounts_folder):
    hots_accounts_folder = f"c:\\Users\\{current_user}\\Documents\\Heroes of the Storm\\Accounts\\"

current_dir = path.dirname(__file__)
config_data = ConfigObj(current_dir + '\\data\\replay.ini')


# ======================================================================
# >> Load
# ======================================================================
def load():
    accounts = get_accounts_list(hots_accounts_folder)
    for x in accounts:
        replay = x.replays_path + list(x.replays)[0]
        break

    replay, protocol = parser.get_replay(replay)

    info = parser.get_match_info(replay, protocol)

    for x in dir(info):
        print(x, "=", getattr(info, x))

    # for player in info.players.values():
        # for x in dir(player):
            # print(x, " = ", getattr(player, x))


# ======================================================================
# >> Get Functions
# ======================================================================
def get_accounts_list(path):
    accounts = []

    folders = listdir(hots_accounts_folder)

    for folder in folders:
        id = folder.split(sep)[-1]
        accounts.append(Account(id))

    return accounts


# ======================================================================
# >> Classes
# ======================================================================
class Account:
    def __init__(self, id):
        self.id = id
        self.replays = []
        self.path = hots_accounts_folder + str(id) + "\\"

        self.get_unique_folder()
        self.replays_path = self.path + self.unique_folder + "\\Replays\Multiplayer\\"

        self.get_replays()

    def get_unique_folder(self):
        tmp = listdir(self.path)
        for folder in tmp:
            folder = folder.split(sep)[-1]
            if folder.startswith('2'):
                break

        self.unique_folder = folder

    def get_replays(self):
        self.replays = set(listdir(self.replays_path))

    def check_new_replays(self):
        replays = set(listdir(self.replays_path))
        check = replays.symmetric_difference(self.replays)
        self.replays = replays
        return check


load()
