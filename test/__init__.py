# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
from random import choice, randint

# Others
import httshots
from httshots import httshots


# ======================================================================
# >> Stats
# ======================================================================
stats_main = ['solo_kill', 'assists', 'deaths']
stats_general = ['structure_damage', 'minion_damage',
         'hero_damage', 'taken_damage', 'healing', 'self_healing', 'merc_camps',
         'experience', 'siege_damage']
stats_mvp = ['mvp', 'xp', 'escapes', 'zerg', 'roots', 'temple', 'skulls', 'gems', 'daredevil_escapes', 'vengeances', 'immortal', 'curse', 'dragon', 'healing', 'silences', 'stuns', 'pushing', 'outnumbered_deaths', 'hat_trick', 'shields', 'siege_damage', 'altar', 'clutch_healing', 'teamfight_healing', 'hero_damage', 'time_on_point', 'outnumbered_deaths', 'cage_unlocks', 'taken_damage', 'teamfight_taken_damage', 'teamfight_hero_damage', 'mercs', 'kill_streak', 'seeds']

maps = ['Альтеракский перевал', 'Башни Рока', 'Драконий Край', 'Вечная Битва',
        'Осквернённые святилища', 'Проклятая лощина', 'Сады ужаса',
        'Завод Вольской', 'Небесный храм', 'Бойня на Браксисе',
        'Гробница Королевы Пауков']

# ======================================================================
# >> Replay
# ======================================================================
count = 0
class TestReplay:
    def __init__(self):
        global count
        blue_win = randint(1, 2)
        red_win = [2, 1][blue_win-1]

        blue_level = randint(10, 20)
        red_level = randint(10, 20)

        self.players = {}
        tmp = list(httshots.data_heroes['names'].keys())

        heroes = tmp[(0+count)*10:(1+count)*10]
        if len(heroes) < 10:
            count = 0
            heroes += tmp[:10-len(heroes)]

        for id in range(10):
            if id < 5:
                player = TestPlayer(id, blue_win, blue_level, heroes[id])
            else:
                player = TestPlayer(id, red_win, red_level, heroes[id])

            self.players[id] = player

        self.details = TestDetails()
        count += 1

class TestPlayer:
    def __init__(self, id, result, level, hero):
        self.userid = id
        self.name = 'Player%s'%id
        self.hero = hero
        if id < 5:
            self.team_id = 0
        else:
            self.team_id = 1

        self.result = result
        self.team_level = level

        self.talents = [1]*7
        self.time = randint(750, 1500)
        for stat in stats_main:
            setattr(self, stat, randint(1, 20))
        for stat in stats_general:
            setattr(self, stat, randint(5000, 250000))
        mpv = choice(stats_mvp)
        setattr(self, 'award_%s'%mpv, 1)
        for mvp in stats_mvp:
            if mvp == mpv:
                continue
            setattr(self, 'award_%s'%mvp, 0)


class TestDetails:
    def __init__(self):
        self.title = choice(maps)

