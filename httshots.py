# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
import asyncio
import hashlib
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
__version__ = "0.8.0"
__author__ = "MrMalina"

current_user = getuser()

# default hots folder
hots_accounts_folder = f"c:\\Users\\{current_user}\\OneDrive\\Documents\\Heroes of the Storm\\Accounts\\"
if not path.isdir(hots_accounts_folder):
    hots_accounts_folder = f"c:\\Users\\{current_user}\\Documents\\Heroes of the Storm\\Accounts\\"

battle_lobby_file = fr"c:\\Users\\{current_user}\AppData\Local\Temp\Heroes of the Storm\TempWriteReplayP1\replay.server.battlelobby"
tracker_events_file = fr"c:\\Users\\{current_user}\AppData\Local\Temp\Heroes of the Storm\TempWriteReplayP1\replay.tracker.events"
icy_url = "https://www.icy-veins.com/heroes/talent-calculator/{}#55.1!{}"
current_dir = path.dirname(__file__)
data_replay = ConfigObj(current_dir + '\\data\\replay.ini')
data_info = ConfigObj(current_dir + '\\data\\info.ini')
data_heroes = ConfigObj(current_dir + '\\data\\heroes.ini')

stream_replays = []
stream_pregame = []
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
    global accounts, strings, language, \
           replay_check_period, hero_data, \
           battle_lobby_hash, config

    config = Config(current_dir + '\\config\\config.ini')
    accounts = get_accounts_list(hots_accounts_folder)
    language = config.language

    strings = Strings(current_dir + '\\data\\strings.ini', language)

    hero_data = HeroData(current_dir + '\\files\\herodata.json')

    if not config.send_previous_battle_lobby:
        if path.isfile(battle_lobby_file):
            file = open(battle_lobby_file, 'rb')
            contents = file.read()
            file.close()
            battle_lobby_hash = hashlib.md5(contents).hexdigest()

    global imgur
    if config.image_upload == 1:
        imgur = ImgurClient(config.imgur_client_id, config.imgur_client_secret)
        print_log('ImgurLogin')

    replay_check_period = config.replay_check_period

    global bot
    bot = bot.TwitchBot(config.twitch_access_token, '!', config.channels)
    bot.run()


# ======================================================================
# >> Functions
# ======================================================================
def get_accounts_list(path: str):
    accounts = []

    folders = listdir(hots_accounts_folder)

    for folder in folders:
        id = folder.split(sep)[-1]
        accounts.append(Account(id))

    return accounts


def print_log(string, *args):
    if config.use_logs:
        print(strings[string].format(*args))


def get_end(number: int, t: int):
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
class HeroData:
    def __init__(self, file_name):
        with open(file_name) as f:
            self.hero_data = json_load(f)

        self.hashtalents = {}

        for hero in self.hero_data.keys():
            talents = self.hero_data[hero]['talents']
            self.hashtalents[hero] = {}
            for x, level in enumerate([1, 4, 7, 10, 13, 16, 20]):
                for talent in talents['level%s'%level]:
                    self.hashtalents[hero][talent['nameId']] = [talent['sort'], x]

    def __getitem__(self, key):
        return self.hero_data[key]

    def get_talent_info_by_name(self, hero_name, talent_name):
        return self.hashtalents[hero_name][talent_name]


class Config:
    def __init__(self, file_name):
        self.config = ConfigObj(file_name)

        self.config.indent_type = '    '
        self.config.encoding = 'UTF-8'
        self.config.initial_comment = ["../httshots/httshots.py"]

        for cvar, value in self.config.items():
            object.__setattr__(self, cvar, self.change_type(value))
            
    def change_type(self, value):
        if type(value) == str:
            if value.isdigit():
                value = int(value)

        return value


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
