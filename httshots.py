# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
import sys

from ftplib import FTP
from getpass import getuser
from hashlib import md5
from configobj import ConfigObj, Section
from json import load as json_load
from os import path, sep, listdir
from imgurpython import ImgurClient
from PIL import ImageFont
from time import strftime
from pathlib import Path


# Httshots
from . import bot
from . import parser, visual, test


# ======================================================================
# >> GLOBAL VARIABLES
# ======================================================================
__name__ = "HTTSHoTS"
__version__ = "0.14.0"
__author__ = "MrMalina"

ICY_URL = "https://www.icy-veins.com/heroes/talent-calculator/{}#55.1!{}"
current_dir = path.dirname(__file__)
data_replay = ConfigObj(current_dir + '\\data\\replay.ini')

stream_replays = []
stream_pregame = []
streak = [0, 0]
accounts = None
strings = None
imgur = None
language = None
replay_check_period = None
battle_lobby_hash = None
tracker_events_hash = None
# Date, time
cur_game = [0, 0]
check_talents_task = None
config = None
fonts = None
paths = None

# ======================================================================
# >> Load
# ======================================================================
def load(argv:list) -> None:
    """Основная функция, запуск бота"""
    global accounts, strings, language, \
           replay_check_period, hero_data, \
           battle_lobby_hash, config, \
           htts_data, imgur, tracker_events_hash, \
           tw_bot, fonts, paths

    config = Config(current_dir + '\\config\\config.ini')
    language = config.language
    strings = Strings(current_dir + '\\data\\strings.ini', language)

    print_log('BotStart')

    # Поиск директории с реплеями
    current_user = getuser()
    check = False
    for folder in config.folder_accounts:
        folder = folder.format(current_user)
        if path.isdir(folder):
            check = True
            config.hots_folder = folder
            print_log('FindHoTSFolder', folder)
            break
    if not check:
        print_log('ErrorFindHoTSFolder')
        return

    # Файлы для текущих талантов и информации о лобби
    tmp = config.folder_hots_temp.format(current_user)
    config.battle_lobby_file = tmp + 'replay.server.battlelobby'
    config.tracker_events_file = tmp + 'replay.tracker.events'

    # Список аккаунтов для поиска сыгранных игр
    accounts = get_accounts_list(folder)

    # Check argv
    if len(argv) > 1:
        if 'IGNORE_PREV_MATCHES' in argv:
            config.add_previous_games = 0
            print_log('ParamIgnorePrevMatches')
        if 'SEND_BATTLE_LOBBY' in argv:
            config.send_previous_battle_lobby = 1
            print_log('ParamSendBattleLobby')
        if 'RU_REPLAY' in argv:
            config.replay_language = 'ru'
            print_log('ParamReplayRu')
        if 'EN_REPLAY' in argv:
            config.replay_language = 'en'
            print_log('ParamReplayEn')

    hero_data = HeroData(current_dir + '\\files\\herodata.json')
    htts_data = DataStrings(current_dir + '\\data\\data.ini', config.replay_language)

    if not config.send_previous_battle_lobby:
        # if check battle_lobby -> all files found
        if path.isfile(config.battle_lobby_file):
            # Battle lobby
            file = open(config.battle_lobby_file, 'rb')
            contents = file.read()
            file.close()
            battle_lobby_hash = md5(contents).hexdigest()

            # Tracker events
            file = open(config.tracker_events_file, 'rb')
            contents = file.read()
            file.close()
            tracker_events_hash = md5(contents).hexdigest()

    # Paths
    paths = HelpCls()
    main_path = Path(current_dir) / "files"
    paths.add('bg', main_path / "background")
    paths.add('stats', main_path / "stats")
    paths.add('score', main_path / "scorescreen")
    paths.add('ttf', main_path / "ttf")
    paths.add('screens', main_path / "screens")
    paths.add('border', main_path / "border")
    paths.add('heroes', main_path / "heroes")
    paths.add('talents', main_path / "talents")
    paths.add('mvp', main_path / "mvp")

    # Fonts
    ascii_ttf = paths.ttf / 'Exo2-Bold.ttf'
    chinese_ttf = paths.ttf / 'HanyiSentyPagoda Regular.ttf'

    fonts = HelpCls()
    fonts.add('small', ImageFont.truetype(ascii_ttf, 12))
    fonts.add('default', ImageFont.truetype(ascii_ttf, 16))
    fonts.add('large', ImageFont.truetype(ascii_ttf, 24))
    fonts.add('big', ImageFont.truetype(ascii_ttf, 46))
    fonts.add('ch_small', ImageFont.truetype(chinese_ttf, 12))
    fonts.add('ch_default', ImageFont.truetype(chinese_ttf, 16))

    # Image upload format
    if config.image_upload == 1:
        imgur = ImgurClient(config.imgur_client_id, config.imgur_client_secret)
        print_log('ImgurLogin')

    elif config.image_upload == 2:
        try:
            ftp = FTP(config.ftp_ip)
            ftp.login(config.ftp_login, config.ftp_passwd)
            ftp.close()
            print_log('FTPLogin', config.site_name)
        except:
            print_log('FTPLoginError', config.site_name)
            return

    replay_check_period = config.replay_check_period

    if config.debug:
        global cur_game
        cur_game = ['-1', '-1']

    # Запуск бота
    tw_bot = bot.TwitchBot(config.twitch_access_token, '!', config.twitch_channel)
    tw_bot.run()


# ======================================================================
# >> Functions
# ======================================================================
def get_accounts_list(folders: str) -> list:
    accounts = []

    folders = listdir(folders)

    for folder in folders:
        id = folder.split(sep)[-1]
        accounts.append(Account(id))

    return accounts


def print_log(string, *args, uwaga=True):
    if config.use_logs and (not config.only_uwaga_logs or uwaga):
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
class HelpCls:
    def __init__(self):
        self.data = {}

    def add(self, name, font):
        self.data[name] = font

    def __getattr__(self, attr):
        return self.data[attr]


class DataStrings:
    def __init__(self, file_name, replay_lang):
        self.data = ConfigObj(file_name)
        self.language = replay_lang

        if not replay_lang in self.data:
            self.language = 'ru'
            print_log('HeroesStringsNoLanguage', replay_lang)

        # need to talents in tracker
        self.icy_en_names = self.data['en'].get('icy_names', {})

        self.data = self.data[self.language]

        self.params = self.data['params']
        self.maps = self.data['maps']
        self.names = self.data['names']
        self.rofl_names = self.data.get('rofl_names', {})
        self.short_names = self.data.get('short_names', {})
        self.data_names = self.data.get('data_names', {})
        self.icy_names = self.data.get('icy_names', {})
        self.data_names_revers = self.data.get('data_names_revers', {})

    def get_eng_hero(self, hero):
        if self.language == 'en':
            return self.names[hero][0]
        else:
            return self.data['en'][hero]

    def get_icy_hero(self, hero, eng_name):
        return self.icy_names.get(hero, eng_name)

    def get_data_name(self, hero):
        return self.data_names.get(hero, hero)

    def get_data_revers_name(self, hero):
        return self.data_names_revers.get(hero, hero)

    def get_short_hero(self, hero):
        return self.short_names.get(hero, hero)

    def get_hero(self, hero, case=None):
        if self.language == 'en':
            return self.names[hero][0]

        if case is not None:
            return self.names[hero][case]
        return self.names[hero]

    def get_hero_by_part(self, hero_name_part):
        for hero in self.names.keys():
            if hero.lower().startswith(hero_name_part):
                return hero

        for hero in self.rofl_names.keys():
            if hero.lower().startswith(hero_name_part):
                hero_name_part = self.rofl_names[hero].lower()
                break

        for hero in self.names.keys():
            if hero.lower().startswith(hero_name_part):
                return hero

    def __getitem__(self, key):
        return self.data[key]


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
            if type(value) == Section:
                for var, val in value.items():
                    object.__setattr__(self, cvar+'_'+var, self.change_type(val))
            else:
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
        self.path = config.hots_folder + str(id) + "/"

        self.get_unique_folder()
        self.replays_path = self.path + self.unique_folder + "/Replays/Multiplayer/"

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

        for _hero in htts_data.rofl_names:
            if _hero.lower().startswith(hero_name_part):
                hero_name_part = htts_data.rofl_names[_hero].lower()
                break

        for player in players:
            if player.hero.lower().startswith(hero_name_part):
                return player
        return None

    def get_players_with_heroes(self):
        return ', '.join([f'{player.name} ({player.hero})' for \
                          player in self.info.players.values()])


# ======================================================================
# >> Start
# ======================================================================
load(sys.argv)
