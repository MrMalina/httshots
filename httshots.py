# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
import sys

from ftplib import FTP, Error as FTP_Error
from getpass import getuser
from hashlib import md5
from json import load as json_load
from os import path, sep, listdir
from time import strftime
from pathlib import Path
from requests import get as req_get
from configobj import ConfigObj, Section
from imgurpython import ImgurClient
from PIL import ImageFont

# Httshots
from . import addons, bot, parser, visual


# ======================================================================
# >> GLOBAL VARIABLES
# ======================================================================
pkg_name = "HTTSHoTS"
pkg_version = "0.22.0"
pkg_author = "MrMalina"

# initialization of constant
ICY_URL = "https://www.icy-veins.com/heroes/talent-calculator/{}#55.1!{}"

# Declaration global variables
stream_replays = []
stream_pregame = []
streak = [0, 0]
cur_game = [0, 0] # [date, time]
accounts = None
strings = None
imgur = None
battle_lobby_hash = None
tracker_events_hash = None
check_talents_task = None
config = None
fonts = None
paths = None
hero_data = None
htts_data = None
tw_bot = None
data_replay = None


# ======================================================================
# >> Load
# ======================================================================
def load(argv:list) -> None:
    """Инициализация модулей и запуск бота"""

    global accounts, strings, \
           hero_data, data_replay, \
           battle_lobby_hash, config, \
           htts_data, imgur, tracker_events_hash, \
           tw_bot, fonts, paths

    current_dir = Path(path.dirname(__file__))
    data_replay = ConfigObj(str(current_dir / 'data' / 'replay.ini'))

    config = Config(str(current_dir / 'config' / 'config.ini'))
    language = config.language
    strings = Strings(str(current_dir / 'data' / 'strings.ini'), language)

    print_log('BotStart', level=5)

    # Проверка новой версии
    check_version = req_get("https://httshots.ru/version")
    if check_version:
        check_version = check_version.text
        if check_version and check_version > pkg_version:
            print_log('NewVersion', pkg_version, check_version, level=4)

    # Поиск директории с реплеями
    current_user = getuser()

    for folder in config.folder_hots_replays:
        hots_folder = folder.format(current_user)
        if path.isdir(hots_folder):
            print_log('FindHoTSFolder', hots_folder, level=3)
            break
    else:
        print_log('ErrorFindHoTSFolder', level=4)
        return

    # Файлы для текущих талантов и информации о лобби
    tmp = config.folder_hots_temp.format(current_user)
    config.battle_lobby_file = tmp + 'replay.server.battlelobby'
    config.tracker_events_file = tmp + 'replay.tracker.events'

    # Список аккаунтов для поиска сыгранных игр
    accounts = get_accounts_list(hots_folder)

    # Check argv
    config.starting_hour = 0
    if len(argv) > 1:
        if 'IGNORE_PREV_MATCHES' in argv:
            config.add_previous_games = 0
            print_log('ParamIgnorePrevMatches', level=3)
        if 'SEND_BATTLE_LOBBY' in argv:
            config.send_previous_battle_lobby = 1
            print_log('ParamSendBattleLobby', level=3)
        if 'RU_REPLAY' in argv:
            config.replay_language = 'ru'
            print_log('ParamReplayRu', level=3)
        elif 'EN_REPLAY' in argv:
            config.replay_language = 'en'
            print_log('ParamReplayEn', level=3)
        if 'URL_TO_CONSOLE' in argv:
            config.duplicate_url_in_console = 1
            print_log('ParamUrlToConsole', level=3)
        if 'STARTING_FROM_HOUR' in argv:
            index = argv.index('STARTING_FROM_HOUR')

            if len(argv) > index+1:
                _time = argv[index+1]

                if not _time.isdigit():
                    print_log('ParamFromTimeErrorType', level=4)
                else:
                    config.starting_hour = int(_time)
                    print_log('ParamFromTime', _time, level=3)

            else:
                print_log('ParamFromTimeErrorNoValue', level=4)

    hero_data = HeroData(str(current_dir / 'files' / 'herodata.json'))
    htts_data = DataStrings(str(current_dir / 'data' / 'data.ini'), config.replay_language)

    if not config.send_previous_battle_lobby:
        # if found battle_lobby -> all files found
        if path.isfile(config.battle_lobby_file):
            # Battle lobby
            with open(config.battle_lobby_file, 'rb') as file:
                contents = file.read()
            battle_lobby_hash = md5(contents).hexdigest()

            # Tracker events
            with open(config.tracker_events_file, 'rb') as file:
                contents = file.read()
            tracker_events_hash = md5(contents).hexdigest()

    # Paths
    paths = HelpCls()
    main_path = current_dir / "files"
    paths.add('bg', main_path / "background")
    paths.add('stats', main_path / "stats")
    paths.add('score', main_path / "scorescreen")
    paths.add('ttf', main_path / "ttf")
    paths.add('upload', main_path / "upload")
    paths.add('border', main_path / "border")
    paths.add('heroes', main_path / "heroes")
    paths.add('talents', main_path / "talents")
    paths.add('mvp', main_path / "mvp")
    paths.add('maps', main_path / "maps")

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
        print_log('ImgurLogin', level=3)

    elif config.image_upload == 2:
        try:
            ftp = FTP(config.ftp_ip)
            ftp.login(config.ftp_login, config.ftp_passwd)
            ftp.close()
            print_log('FTPLogin', config.site_name, level=3)
        except FTP_Error as e:
            print_log('FTPLoginError', config.site_name, level=4)
            raise e

    # Загрузка аддонов
    addons.load_addons(config.config['addons'])

    # Список имён аккаунтов должен быть списком, а не строкой
    acc_names = config.accounts
    if isinstance(acc_names, str):
        config.accounts = (acc_names, )

    # Запуск бота
    tw_channel = config.twitch_channel
    if isinstance(tw_channel, str):
        tw_channel = (tw_channel, )
    tw_bot = bot.TwitchBot(config.twitch_access_token, '!', tw_channel)

    bot.events.bot_initialized(tw_bot)

    tw_bot.run()


# ======================================================================
# >> Functions
# ======================================================================
def get_accounts_list(hots_folder: str) -> list:
    _accounts = []

    account_folders = listdir(hots_folder)

    for folder in account_folders:
        _id = folder.split(sep)[-1]
        acc = Account(hots_folder, _id)
        if acc.regions:
            _accounts.append(acc)

    return _accounts


def print_log(string, *args, level=0):
    if config.log_level <= level:
        print(strings[string].format(*args))


def get_end(number: int, t: str):
    i = number % 100
    if 11 <= i <= 19:
        return strings[t][2]

    i = i % 10
    if i == 1:
        y = strings[t][0]
    elif i in {2, 3, 4}:
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
            print_log('HeroesStringsNoLanguage', replay_lang, level=4)

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

        return None

    def __getitem__(self, key):
        return self.data[key]


class HeroData:
    def __init__(self, file_name):
        with open(file_name, encoding="ANSI") as f:
            self.hero_data = json_load(f)

        self.hashtalents = {}

        for hero in self.hero_data.keys():
            talents = self.hero_data[hero]['talents']
            self.hashtalents[hero] = {}
            for x, level in enumerate([1, 4, 7, 10, 13, 16, 20]):
                for talent in talents['level'+str(level)]:
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

        for cvar, value in self.config.items():
            if isinstance(value, Section):
                for var, val in value.items():
                    object.__setattr__(self, cvar+'_'+var, self.change_type(val))
            else:
                object.__setattr__(self, cvar, self.change_type(value))

    def change_type(self, value):
        if isinstance(value, str):
            if value.isdigit():
                return int(value)

        return value


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Strings:
    def __init__(self, _path, lang):
        _strings = ConfigObj(_path)

        if lang in _strings:
            self.strings = _strings[lang]
        else:
            self.strings = _strings['ru']

        if config.use_colors:
            for key, string in self.strings.items():
                if isinstance(string, str):
                    self.strings[key] = self.replace_colors(string)
        else:
            for key, string in self.strings.items():
                if isinstance(string, str):
                    self.strings[key] = self.remove_colors(string)

    def remove_colors(self, string):
        string = string.replace('#cyan', '')
        string = string.replace('#green', '')
        string = string.replace('#red', '')
        string = string.replace('#blue', '')
        string = string.replace('#gold', '')
        string = string.replace('#viol', '')
        string = string.replace('#def', '')
        return string

    def replace_colors(self, string):
        string = string.replace('#cyan', Colors.OKCYAN)
        string = string.replace('#green', Colors.OKGREEN)
        string = string.replace('#red', Colors.FAIL)
        string = string.replace('#blue', Colors.OKBLUE)
        string = string.replace('#gold', Colors.WARNING)
        string = string.replace('#viol', Colors.HEADER)
        string = string.replace('#def', Colors.ENDC)
        return string

    def __getitem__(self, key):
        return self.strings.get(key, f"No string '{key}' in strings.ini")

    def __call__(self, key, *args):
        _str = self.strings.get(key, f"No string '{key}' in strings.ini")
        return _str.format(*args)


class Account:
    class Replays:
        def __init__(self, replay_path):
            self.replay_path = replay_path
            self.replays = self.get_replays()

        def get_replays(self):
            current_date = strftime('%Y-%m-%d')
            return set(filter(lambda x: x.startswith(current_date), listdir(self.replay_path)))

        def check_new_replays(self):
            replays = self.get_replays()
            check = replays.symmetric_difference(self.replays)
            if check:
                self.replays = replays
                if not path.isfile(self.replay_path + list(check)[0]):
                    return 0
                return self.replay_path + list(check)[0]
            return 0

    def __init__(self, hots_folder, _id):
        self.id = _id
        self.path = hots_folder + str(_id) + "/"
        self.regions = []
        self.replays = set()
        self.get_replays()

        folders = self.get_unique_acc_folders()
        for region_folder in folders:
            replay_path = self.path + region_folder + "/Replays/Multiplayer/"
            self.regions.append(self.Replays(replay_path))

        if len(self.regions) == 1:
            self.check_new_replays = lambda: self.regions[0].check_new_replays()

    def get_all_replays(self):
        _rets = []
        for region in self.regions:
            _rets += [region.replay_path + x for x in region.get_replays()]
        return _rets

    def get_replays(self):
        for region in self.regions:
            self.replays.update(region.get_replays())
        return self.replays

    def check_new_replays(self):
        x = list(filter(lambda x: x != 0, map(lambda x: x.check_new_replays(), self.regions)))
        if x:
            return x[0]
        return 0

    def get_unique_acc_folders(self):
        tmp = listdir(self.path)
        _folders = []
        for folder in tmp:
            folder = folder.split(sep)[-1]
            # Для любого региона
            if 'Hero' in folder:
                _folders.append(folder)
        return _folders


class StreamReplay:
    def __init__(self, title, me, info):
        self.title = title
        self.account = me
        self.info = info

        self.heroes = map(lambda x: x.hero, self.info.players.values())
        status = strings['GameResult'+['Win','Lose'][int(me.result)-1]]
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
