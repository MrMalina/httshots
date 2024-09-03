# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
from configobj import ConfigObj
import mpyq

# Others
import heroprotocol
from heroprotocol import versions

from . import image


# ======================================================================
# >> Teams
# ======================================================================
class Team:
    def __init__(self):
        self.players = []
        self.kills = 0
        self.deaths = 0
        self.xp = 0
        self.heals = 0
        self.self_heal = 0
        self.deal_damage = 0
        self.take_damage = 0
        self.siege_damage = 0
        self.death_time = 0
        self.minion_damage = 0
        self.structure_damage = 0

        self.lkills = []
        self.ldeaths = []
        self.lxps = []
        self.lheals = []
        self.lself_heals = []
        self.ldeal_damage = []
        self.ltake_damage = []
        self.ldeath_time = []



class MatchInfo:
    def __init__(self):
        self.kills = 0
        self.deaths = 0
        self.xp = 0
        self.heals = 0
        self.self_heal = 0
        self.deal_damage = 0
        self.take_damage = 0
        self.death_time = 0


def prepare_visual_info(info):
    team_blue = Team()
    team_red = Team()
    match_info = MatchInfo()

    for player in info.players.values():
        if player.team_id == 0:
            tm = team_blue
        else:
            tm = team_red

        print(player.name)
        print(player.solo_kill)

        tmp = player.solo_kill

        tm.kills += tmp
        if tmp > match_info.kills:
            match_info.kills = tmp
        tm.lkills.append(tmp)

        tmp = player.deaths

        tm.deaths += tmp
        if tmp > match_info.deaths:
            match_info.deaths = tmp
        tm.ldeaths.append(tmp)

        tmp = player.experience

        tm.xp += tmp
        if tmp > match_info.xp:
            match_info.xp = tmp
        tm.lxps.append(tmp)

        tmp = player.healing

        tm.heals += tmp
        if tmp > match_info.heals:
            match_info.heals = tmp
        tm.lheals.append(tmp)

        tmp = player.self_healing

        tm.self_heal += tmp
        if tmp > match_info.self_heal:
            match_info.self_heal = tmp
        tm.lself_heals.append(tmp)

        tmp = player.hero_damage

        tm.deal_damage += tmp
        if tmp > match_info.deal_damage:
            match_info.deal_damage = tmp
        tm.ldeal_damage.append(tmp)

        tmp = player.taken_damage

        tm.take_damage += tmp
        if tmp > match_info.take_damage:
            match_info.take_damage = tmp
        tm.ltake_damage.append(tmp)

        tmp = player.death_time

        tm.death_time += tmp
        if tmp > match_info.death_time:
            match_info.death_time = tmp

        tm.ldeath_time.append(tmp)

        # tm.xp += player.experience
        # tm.heals += player.healing
        # tm.self_heal += player.self_healing
        # tm.deal_damage += player.hero_damage
        # tm.take_damage += player.taken_damage
        # tm.siege_damage += player.siege_damage
        # tm.death_time += player.death_time
        # tm.structure_damage += player.structure_damage

    return team_blue, team_red, match_info


def create_bar_kills(tb, tr, mi):
    # bar_kills_blue = image.create_bar(tb.lkills, 0, mi.kills, 'Убийства команды')
    # bar_kills_blue = image.create_bar(tb.ldeal_damage, 0, mi.deal_damage, 'Урон команды')
    bar_kills_blue = image.create_bar(tb.ldeath_time, 0, mi.death_time, 'Время смерти команды')



    
