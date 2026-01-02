# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
import asyncio
import asqlite

from urllib.request import urlopen
from ftplib import FTP, Error as FTP_Error
from getpass import getuser
from hashlib import md5
from json import load as json_load
from os import path, sep, listdir
from time import strftime
from pathlib import Path
from configobj import ConfigObj, Section
from imgurpython import ImgurClient
from PIL import ImageFont

# Httshots
import httshots
from . import addons, bot, parser, visual


# ======================================================================
# >> GLOBAL VARIABLES
# ======================================================================
# initialization of constant
ICY_URL = "https://www.icy-veins.com/heroes/talent-calculator/{}#55.1!{}"
LATEST_RELEASE_URL = "https://api.github.com/repos/MrMalina/httshots/releases/latest"
HOTS_VERSION = "95918"
STOPPED = 0

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
current_dir = None


# ======================================================================
# >> Load
# ======================================================================
def load(argv:list, full_load) -> None:
    """Инициализация модулей и запуск бота"""

    global accounts, strings, \
           hero_data, data_replay, \
           battle_lobby_hash, config, \
           htts_data, imgur, tracker_events_hash, \
           tw_bot, fonts, paths, current_dir

    current_dir = Path(path.dirname(__file__))

    config = Config(str(current_dir / 'config' / 'config.ini'))
    language = config.language
    strings = Strings(str(current_dir / 'data' / 'strings.ini'), language)

    print_log('BotStart', level=5)

    data_replay = ConfigObj(str(current_dir / 'data' / 'replay.ini'))

    # Проверка новой версии
    with urlopen(LATEST_RELEASE_URL, timeout=2) as url:
        data = json_load(url)
        tag_name = data['tag_name']
        version = tag_name[1:]
        if version > httshots.pkg_version:
            print_log('NewVersion', httshots.pkg_version, version, level=4)

    # Параметры запуска
    get_twitch_id = 0
    if len(argv) > 1:
        if 'GET_TWITCH_ID' in argv:
            index = argv.index('GET_TWITCH_ID')
            if len(argv) > index+1:
                user = argv[index+1]
                get_twitch_id = user

        if 'IGNORE_PREV_MATCHES' in argv:
            config.add_previous_games = 0
            print_log('ParamIgnorePrevMatches', level=3)
        if 'SEND_BATTLE_LOBBY' in argv:
            config.send_previous_battle_lobby = 1
            print_log('ParamSendBattleLobby', level=3)
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

    if get_twitch_id:
        async def runner_get_id() -> None:
            async with bot.twitchio.Client(client_id=str(config.twitch_client_id),
                                       client_secret=str(config.twitch_client_secret)) as client:
                await client.login()
                user = await client.fetch_users(logins=[get_twitch_id])
                for u in user:
                    print(f"User: {u.name} - ID: {u.id}")
                return

        try:
            asyncio.run(runner_get_id())
        except KeyboardInterrupt:
            ...

        return

    # Поиск директории с реплеями
    current_user = getuser()

    # Список директорий для поиска реплеев должен быть списком, а не строкой
    folder_hots_replays = config.folder_hots_replays
    if isinstance(folder_hots_replays, str):
        folder_hots_replays = (folder_hots_replays, )

    # Определение директории с реплеями хотса
    for folder in folder_hots_replays:
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

    hero_data = HeroData(str(current_dir / 'files' / 'herodata.json'))
    htts_data = DataStrings(str(current_dir / 'data' / 'data.ini'), language)

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
    paths.add('utils', main_path / "utils")
    paths.add('ttf', main_path / "ttf")
    paths.add('upload', main_path / "upload")
    paths.add('border', main_path / "border")
    paths.add('heroes', main_path / "heroes")
    paths.add('talents', main_path / "talents")
    paths.add('mvp', main_path / "mvp")
    paths.add('data', main_path / "data")

    # Fonts
    ascii_ttf = paths.ttf / 'Exo2-Bold.ttf'
    # Китайский шрифт используется, если ник не соответствует регулярке [a-zA-Zа-яА-Я0-9]*
    chinese_ttf = paths.ttf / 'HanyiSentyPagoda Regular.ttf'

    fonts = HelpCls()
    fonts.add('small', ImageFont.truetype(ascii_ttf, 12))
    fonts.add('default', ImageFont.truetype(ascii_ttf, 16))
    fonts.add('large', ImageFont.truetype(ascii_ttf, 24))
    fonts.add('big', ImageFont.truetype(ascii_ttf, 46))
    fonts.add('ch_small', ImageFont.truetype(chinese_ttf, 12))
    fonts.add('ch_default', ImageFont.truetype(chinese_ttf, 16))

    if not full_load:
        return

    # Image upload format
    if config.image_upload == 1:
        imgur = ImgurClient(config.imgur_client_id, config.imgur_client_secret)
        print_log('ImgurLogin', level=3)

    elif config.image_upload == 2:
        try:
            ftp = FTP(config.ftp_ip)
            ftp.login(config.ftp_login, config.ftp_passwd)
            ftp.close()
            print_log('FTPLogin', config.ftp_site_name, level=3)
        except FTP_Error as e:
            print_log('FTPLoginError', config.ftp_site_name, level=4)
            raise e

    # Вывод какие версии реплеев поддерживаются
    print_log('BotHoTSVersions', HOTS_VERSION, level=3)

    # Загрузка аддонов
    addons.load_addons(config.config['addons'])

    # Список имён аккаунтов должен быть списком, а не строкой
    acc_names = config.accounts
    if isinstance(acc_names, str):
        config.accounts = (acc_names, )

    async def runner() -> None:
        global tw_bot
        _path = paths.data / "tokens.db"
        async with (asqlite.create_pool(str(_path)) as tdb,
                   bot.TwitchBot(str(config.twitch_client_id),
                                 str(config.twitch_client_secret),
                                 str(config.twitch_bot_id),
                                 str(config.twitch_owner_id),
                                 "!", tdb) as tw_bot):

            await tw_bot.setup_database()
            await tw_bot.start()

    try:
        asyncio.run(runner())
    except KeyboardInterrupt:
        ...


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


def print_other_log(string, *args, level=0):
    if config.log_level <= level:
        print(string.format(*args))


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
    def add(self, name, font):
        self.__dict__[name] = font

    def __getattr__(self, attr):
        return self.__dict__[attr]


class DataStrings:
    class Params:
        def __setattr__(self, name, value):
            self.__dict[name] = value
        def __getattr__(self, name):
            return self.__dict__[name]

    def __init__(self, file_name, language):
        self.data = ConfigObj(file_name)
        self.plang = language

        if not language in self.data:
            self.plang = 'ru'
            print_log('HeroesStringsNoLanguage', language, level=4)

        self.data_names = self.data['all']['data_names']

        self.params = {}
        self.all_rofl_names = {}
        heroes = self.data['all']['heroes']
        maps = self.data['all']['maps']
        self.reverse_heroes = {hero: o_hero for o_hero, t_hero in heroes.items() for hero in t_hero}
        self.reverse_maps = {map_: o_map for o_map, t_map in maps.items() for map_ in t_map}

        for lang in self.data:
            if lang == 'all':
                continue

            if 'params' in self.data[lang]:
                self.params |= self.data[lang]['params']

            if 'rofl_names' in self.data[lang]:
                self.all_rofl_names |= self.data[lang]['rofl_names']

            if not 'short_names' in self.data[lang]:
                self.data[lang]['short_names'] = {}

    def get_hero(self, name):
        return self.reverse_heroes.get(name, name)

    def get_translate_hero(self, name, case):
        hero = self.reverse_heroes.get(name, name)
        if self.plang == 'en':
            return hero

        if hero in self.data[self.plang]['names']:
            return self.data[self.plang]['names'][hero][case]

        return 'NoName'

    def get_map(self, name):
        return self.reverse_maps.get(name, name)

    def get_translate_map(self, name):
        map_name = self.reverse_maps.get(name, name)

        if self.plang == 'en':
            return map_name

        if map_name in self.data[self.plang]['maps']:
            return self.data[self.plang]['maps'][map_name]

        return 'NoName'

    def get_icy_hero(self, name):
        if name in self.data['all']['icy_names']:
            return self.data['all']['icy_names'][name]
        return self.remove_symbols(name)

    def remove_symbols(self, name):
        return name.replace('.', '').replace('-', '').replace(' ', '').replace("'", '').lower()

    def get_data_name(self, name):
        return self.data_names.get(name, name)

    def get_short_hero(self, name):
        return self.data[self.plang]['short_names'].get(name, name)

    def get_hero_by_part(self, part_name):
        part_name = part_name.lower()
        for hero in self.reverse_heroes:
            if hero.lower().startswith(part_name):
               return self.reverse_heroes[hero]

        for rofl in self.all_rofl_names:
            if rofl.startswith(part_name):
                return self.all_rofl_names[rofl]

        return None


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

        self.starting_hour = 0
        self.spectator_mode = 0

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

        self.language = config.language
        self.url_draft = None

        self.heroes = map(lambda x: x.hero, self.info.players.values())
        status = strings['GameResult'+['Win','Lose'][int(me.result)-1]]

        hero_name = htts_data.get_translate_hero(self.account.hero, 0)
        map_name = htts_data.get_translate_map(self.info.details.title)

        self.short_info = f"{map_name} - {hero_name} - {status}"

        self.players = self.info.players.values()

        self._heroes = [(x, x.hero) for x in self.players]

    def try_find_hero(self, part_name):
        part_name = htts_data.get_hero_by_part(part_name)
        if part_name is None:
            return None

        for player, hero in self._heroes:
            if hero.startswith(part_name):
                return player

        return None

    def get_players_with_heroes(self):
        return ', '.join([f'{player.name} ({player.hero})' for \
                          player in self.info.players.values()])
