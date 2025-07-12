# ======================================================================
# >> Imports
# ======================================================================

# HttsHots
import httshots
from httshots import httshots

from . import parse



# ======================================================================
# >> Classes
# ======================================================================
class TrackerEvents:
    def __init__(self, event, players, userids):
        # Перевернуть?
        cfg = httshots.data_replay['instance-list']

        # Это NNet.Replay.Tracker.SScoreResultEvent
        for info in event:
            name = parse.decode_string(info['m_name'])
            if name in cfg:
                for n, player in zip(userids, players):
                    setattr(player, cfg[name], info['m_values'][n][0]['m_value'])

        for n, player in zip(userids, players):
            player.time = info['m_values'][n][0]['m_time']
            player.talents = [player.talent1, player.talent2, player.talent3,
                              player.talent4, player.talent5, player.talent6,
                              player.talent7]

class Lobby:
    class Ban:
        def __init__(self, info):
            hero = parse.decode_string(info['m_hero'])
            if hero == 'NONE': hero = 'skipban'
            self.hero = hero
            self.team = info['m_controllingTeam']
    class Pick:
        def __init__(self, info):
            self.hero = parse.decode_string(info['m_hero'])
            self.player = info['m_controllingPlayer']

    def __init__(self, events):
        self.bans = []
        self.picks = []
        for event in events:
            if event['_eventid'] == 13:
                ban = self.Ban(event)
                self.bans.append(ban)
            elif event['_eventid'] == 14:
                pick = self.Pick(event)
                self.picks.append(pick)


class Header(parse.Parse):
    def __init__(self, data):
        self.parse_data('headers', data)

        self.full_version = f"{self.version.major}.{self.version.minor}." \
                            f"{self.version.revision} ({self.version.build})"

    def __repr__(self):
        return self.full_version


class InitData(parse.Parse):
    def __init__(self, data, players):
        data = data['m_syncLobbyState']

        self.parse_data("initdata-gamedescription", data['m_gameDescription'])

        self.parse_data("initdata-lobbystate", data['m_lobbyState'])

        data = data['m_lobbyState']['m_slots']
        for info in data:
            userid = info['m_userId']

            if userid is None or userid >= 10:
                continue

            player = players[userid]
            player.hero_level = 0

            player.color_pref = info['m_colorPref']['m_color']
            player.race_pref = info['m_racePref']['m_race']
            player.diffuculty = info['m_difficulty']
            player.ai_build = info['m_aiBuild']
            player.logo_index = info['m_logoIndex']
            player.skin = parse.decode_string(info['m_skin'])
            player.mount = parse.decode_string(info['m_mount'])
            player.tandem_leader_userid = info['m_tandemLeaderUserId']
            player.has_silence_penalty = info['m_hasSilencePenalty']
            player.has_voice_silence_penalty = info['m_hasVoiceSilencePenalty']
            player.is_blizzard_staff = info['m_isBlizzardStaff']
            player.has_active_boost = info['m_hasActiveBoost']
            player.banner = parse.decode_string(info['m_banner'])
            player.spray = parse.decode_string(info['m_spray'])
            player.announcer_pack = parse.decode_string(info['m_announcerPack'])
            player.voice_line = parse.decode_string(info['m_voiceLine'])
            hero_mastery = info['m_heroMasteryTiers']
            player.hero_mastery_tiers = {x['m_hero']:x['m_tier'] for x in hero_mastery}


    def __repr__(self):
        return f'{self.game_type}'


class Details(parse.Parse):
    def __init__(self, data):
        _players = data['m_playerList']

        self.players = {}

        for userid, info in enumerate(_players):
            self.players[userid] = Player(userid, info)

        _players = sorted(self.players.values(), key=lambda x: x.team_id)

        self.sort_ids = [x.userid for x in _players]

        self.parse_data('details', data)

        self.title = httshots.htts_data.get_map(self.title)

    def __repr__(self):
        return f'{self.title}'


class Player:
    def __init__(self, userid, info):
        """Игровой пользователь

            :property userid:
                Идентификатор пользователя от 0 до 9.
                В явном виде не указывается, но порядок пользователей в
                replay.details соответствует их userid в других данных реплея
            
            :property name:
                Имя пользователя

            :property toon:
                Информация о регионе и профиле пользователя

            :property race:
                Раса? Всегда равна 0
                Встречается в replay.initdata, но тоже равно всегда равно 0
            
            :property color:
                Цвет игрока? Класс Color, забавно, но m_b линейно растёт
                от 1 до 10, а m_r меняет значение от 0 до 2 не
                в очень понятном порядке

            :property control:
                Кто контролирует героя
                2 - игрок
                3 - бот

            :property team_id:
                Идентификатор команды
                0 - синие
                1 - красные

            :property observe:
                Является ли игрок наблюдателем

            ...

        """

        self.userid = userid
        self.name = info['m_name'].decode('utf8')
        self.toon = Region(info['m_toon'])
        self.race = parse.decode_string(info['m_race'])
        self.color = Color(info['m_color'])
        self.control = info['m_control']
        self.team_id = info['m_teamId']
        self.observer = info['m_observe']
        self.result = info['m_result']
        self.working_set_slot_id = info['m_workingSetSlotId']
        hero = parse.decode_string(info['m_hero'])
        self.hero = httshots.htts_data.get_hero(hero)

    def __repr__(self):
        return f"{self.userid} - {self.name} - {self.hero}"


class Color:
    def __init__(self, tmp):
        self.a = tmp['m_a']
        self.r = tmp['m_r']
        self.g = tmp['m_g']
        self.b = tmp['m_b']

    def __repr__(self):
        return f'{self.r} {self.g} {self.b} {self.a}'


class Region:
    """Класс для описания региона пользователя
    """

    def __init__(self, info):
        """Полностью совпадает с директорией, где располагаются реплеи пользователя
           Например, 2-Hero-1-992291

            :param dict info:
                Словарь из replay.details -> m_playerList -> m_toon

            :var region:
                Регион пользователя
                1 - Америка
                2 - Европа
                3 - ???

            :var program_id:
                ID программы - всегда Hero

            :var realm:
                Игровой мир?

            :var id:
                Идентификатор чего-то
        """

        self.region = info['m_region']
        self.program_id = parse.decode_string(info['m_programId'])
        self.realm = info['m_realm']
        self.id = info['m_id']

        self.toon = f'{self.region}-{self.program_id}-{self.realm}-{self.id}'

    def __repr__(self):
        return self.toon
