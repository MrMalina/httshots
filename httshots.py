# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
import asyncio
from getpass import getuser
from imgurpython import ImgurClient
from time import strftime

from configobj import ConfigObj
from os import path, sep, listdir
from json import load as json_load


# Httshots
from . import bot, parser, score, test


# ======================================================================
# >> GLOBAL VARIABLES
# ======================================================================
__name__ = "HTTSHoTS"
__version__ = "0.6.0"
__author__ = "MrMalina"

current_user = getuser()

# default hots folder
hots_accounts_folder = f"c:\\Users\\{current_user}\\OneDrive\\Documents\\Heroes of the Storm\\Accounts\\"
if not path.isdir(hots_accounts_folder):
    hots_accounts_folder = f"c:\\Users\\{current_user}\\Documents\\Heroes of the Storm\\Accounts\\"

battle_lobby_file = r"c:\Users\Pytho\AppData\Local\Temp\Heroes of the Storm\TempWriteReplayP1\replay.server.battlelobby"
icy_url = "https://www.icy-veins.com/heroes/talent-calculator/{}#55.1!{}"
current_dir = path.dirname(__file__)
config = ConfigObj(current_dir + '\\config\\config.ini')
data_replay = ConfigObj(current_dir + '\\data\\replay.ini')
data_info = ConfigObj(current_dir + '\\data\\info.ini')
data_heroes = ConfigObj(current_dir + '\\data\\heroes.ini')

stream_replays = []
streak = [0, 0]
accounts = None
strings = None
imgur = None
language = None
replay_check_period = None
battle_lobby_hash = None
herodata = None


# ======================================================================
# >> Load
# ======================================================================
def load():
    global accounts, strings, language, replay_check_period, log_level, herodata
    accounts = get_accounts_list(hots_accounts_folder)
    language = config['LANGUAGE']
    log_level = int(config['LOG_LEVEL'])
    strings = Strings(current_dir + '\\data\\strings.ini', language)
    replay_check_period = int(config['REPLAY_CHECK_PERIOD'])

    with open(current_dir + '\\files\\herodata.json') as f:
        herodata = json_load(f)

    global imgur
    if config['IMGUR_USE']:
        imgur = ImgurClient(config['IMGUR_CLIENT_ID'], config['IMGUR_CLIENT_SECRET'])
        print_log('ImgurLogin', 1)
    else:
        print_log('ImgurNoUsing', 1)

    global bot
    bot = bot.TwitchBot(config['TWITCH_ACCESS_TOKEN'], '!', config['CHANNELS'])
    bot.run()


# ======================================================================
# >> Functions
# ======================================================================
def get_accounts_list(path):
    accounts = []

    folders = listdir(hots_accounts_folder)

    for folder in folders:
        id = folder.split(sep)[-1]
        accounts.append(Account(id))

    return accounts


def print_log(string, level, *args):
    if level <= log_level:
        print(strings[string].format(*args))


def get_end(number, t):
    inumber = number % 100
    if inumber >= 11 and inumber <=19:
        y = strings[t][2]
    else:
        iinumber = inumber % 10
        if iinumber == 1:
            y = strings[t][0]
        elif iinumber == 2 or iinumber == 3 or iinumber == 4:
            y = strings[t][1]
        else:
            y = strings[t][2]
    return y


# ======================================================================
# >> Classes
# ======================================================================
class Strings:
    def __init__(self, path, lang):
        strings = ConfigObj(path)

        if lang in strings:
            self.strings = strings[lang]
        else:
            self.strings = strings['ru']

    def __getitem__(self, key):
        return self.strings.get(key, f"No string '{key}' in strings.ini")

    def __call__(self, key, *args):
        _str = self.strings.get(key, f"No string '{key}' in strings.ini")
        return _str.format(*args)


class Account:
    def __init__(self, id):
        self.id = id
        self.path = hots_accounts_folder + str(id) + "\\"

        self.get_unique_folder()
        self.replays_path = self.path + self.unique_folder + "\\Replays\Multiplayer\\"

        self.replays = self.get_replays()

    def get_unique_folder(self):
        tmp = listdir(self.path)
        for folder in tmp:
            folder = folder.split(sep)[-1]
            if folder.startswith('2'):
                break

        self.unique_folder = folder

    def get_replays(self):
        current_date = strftime('%Y-%m-%d')
        return set(filter(lambda x: x.startswith(current_date), listdir(self.replays_path)))

    def check_new_replays(self):
        replays = self.get_replays()
        check = replays.symmetric_difference(self.replays)
        if check:
            self.replays = replays
            if not path.isfile(self.replays_path + list(check)[0]):
                return 0
            return self.replays_path + list(check)[0]
        return 0


class StreamReplay:
    def __init__(self, title, me, info):
        self.title = title
        self.account = me
        self.info = info

        self.heroes = map(lambda x: x.hero, self.info.players.values())
        status = strings['GameResult%s'%{1:'Win',2:'Lose'}[int(me.result)]]
        self.short_info = f"{self.info.details.title} - {self.account.hero} - {status}"

    def try_find_hero(self, hero_name_part):
        players = self.info.players.values()
        for player in players:
            if player.hero.lower().startswith(hero_name_part):
                return player

        for _hero in data_heroes['rofl_names']:
            if _hero.lower().startswith(hero_name_part):
                hero_name_part = data_heroes['rofl_names'][_hero].lower()
                break

        for player in players:
            if player.hero.lower().startswith(hero_name_part):
                return player
        return None

    def get_players_with_heroes(self):
        return ', '.join([f'{player.name} ({player.hero})' for player in self.info.players.values()])


# ======================================================================
# >> Start
# ======================================================================
load()
