# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
from twitchio.ext import commands

# httshots
from httshots import httshots
from . import tracker


# ======================================================================
# >> Functions
# ======================================================================
class BotCommands(commands.Component):
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(rate=1, per=2)
    @commands.command(aliases=("матч", ))
    async def game(self, ctx: commands.Context,
                    hero: str | None = None,
                    info: str | None = None):
        if not len(httshots.stream_replays):
            text = httshots.strings['GameNotFound']
            await ctx.send(text)
            return

        _game = httshots.stream_replays[-1]
        if hero is None:
            text = httshots.strings['GameInfo'].format(_game.short_info)
            await ctx.send(text)

        else:
            hero = hero.lower().strip()
            if hero in ('heroes', 'герои'):
                blue = [httshots.htts_data.get_translate_hero(x.hero, 0) \
                        for x in _game.info.players.values() if x.team_id == 0]
                red = [httshots.htts_data.get_translate_hero(x.hero, 0) \
                        for x in _game.info.players.values() if x.team_id == 1]
                text = httshots.strings['GameHeroes'].format(', '.join(blue), ', '.join(red))
                await ctx.send(text)
                return

            if hero in ('счёт', 'счет', 'score'):
                kills = [0, 0]
                for _player in _game.info.players.values():
                    if _player.team_id == 0:
                        team_level_blue = _player.team_level
                        kills[0] += _player.solo_kill
                    else:
                        team_level_red = _player.team_level
                        kills[1] += _player.solo_kill

                text = httshots.strings['GameScore'].format(team_level_blue, team_level_red,
                                                            kills[0], kills[1])
                await ctx.send(text)
                return

            if hero in ('draft', 'драфт'):
                bans = _game.info.lobby.bans
                if bans:
                    if _game.url_draft is not None:
                        text = httshots.strings['GameDraft'].format(_game.url_draft)
                    else:
                        text = httshots.strings['GameNoDraft']
                else:
                    text = httshots.strings['GameNoBans']
                await ctx.send(text)
                return

            if hero in ('bans', 'баны'):
                bans = _game.info.lobby.bans
                if bans:
                    # if _game.url_draft is not None:
                        # text = httshots.strings['GameDraft'].format(_game.url_draft)
                    # else:
                    blue_bans = []
                    red_bans = []
                    for ban in bans:
                        hero = httshots.htts_data.get_hero(ban.hero)
                        hero  = httshots.htts_data.get_translate_hero(hero, 0)
                        if ban.team == 1:
                            blue_bans.append(hero)
                        else:
                            red_bans.append(hero)
                    text = httshots.strings['GameBans'].format(', '.join(blue_bans),
                                                               ', '.join(red_bans))
                else:
                    text = httshots.strings['GameNoBans']
                await ctx.send(text)
                return

            if hero in ('meat', 'мясо'):
                player = _game.try_find_hero('Butcher')
                if player is None:
                    text = httshots.strings['GameNoButcherInGame'].format(ctx.author.name)

                else:
                    meats = 0
                    still_meats = 0
                    draise_meats = 0

                    # ?????

                    loops = list(_game.info.game_loops.keys())
                    loops.sort()

                    for loop in loops:
                        events = _game.info.game_loops[loop]
                        for event, unit in events:
                            if event == 'DeathUnit':
                                if unit.is_meat() and not unit.was_picked():
                                    draise_meats += 20 if '20' in unit.name else 1
                                elif unit.is_meat() and unit.was_picked():
                                    meats += 20 if '20' in unit.name else 1

                            if event == 'DeathHero':
                                if unit.player_id == player.userid+1:
                                    if meats < 200:
                                        if meats >= 15:
                                            still_meats += 15
                                        else:
                                            still_meats += meats
                                        meats = max(0, meats-15)

                    text = httshots.strings['GameButcherLoseMeats'].format(player.name, draise_meats, still_meats)
                await ctx.send(text)
                return

            player = _game.try_find_hero(hero.lower().strip())
            if player is None:
                text = httshots.strings['GameNotFoundHero'].format(ctx.author.name)
                await ctx.send(text)
                return

            if not info:
                hero = player.hero
                hero_name = httshots.htts_data.get_translate_hero(hero, 1)
                hots_hero_name = httshots.htts_data.remove_symbols(hero)
                talents = ''.join(map(str, player.talents))
                tmp = f" [T{talents},{hots_hero_name}]"
                icy_hero = httshots.htts_data.get_icy_hero(hero).lower()
                icy_url = httshots.ICY_URL.format(icy_hero, talents.replace('0', '-'))
                text = httshots.strings['GameHeroTalents'].format(hero_name, tmp, icy_url)
                await ctx.send(text)
                return

            info = info.strip().lower()
            info = httshots.htts_data.params.get(info, info)
            if info in ('счёт', 'счет', 'score'):
                hero = httshots.htts_data.get_translate_hero(player.hero, 0)
                text = httshots.strings['GameHeroScore'].format(player.name, hero,
                                                                player.solo_kill, player.deaths,
                                                                player.assists)
            else:
                value = getattr(player, info, None)
                if value is None:
                    text = httshots.strings['GameHeroInfoNotFound'].format(info)
                else:
                    hero = httshots.htts_data.get_translate_hero(player.hero, 0)
                    text = httshots.strings['GameHeroInfo'].format(hero, info, value)
            await ctx.send(text)


    @commands.cooldown(rate=1, per=2)
    @commands.command(aliases=("матчи", ))
    async def games(self, ctx: commands.Context):
        matches = len(httshots.stream_replays)
        if not matches:
            text = httshots.strings['GameNotFound']
            await ctx.send(text)
            return

        wins = len(list(filter(lambda x: x.account.result == 1, httshots.stream_replays)))
        loses = len(list(filter(lambda x: x.account.result == 2, httshots.stream_replays)))
        url_games = httshots.stream_replays[-1].url_games

        if matches == 1:
            win_text = httshots.get_end(wins, 'Wins')
            lose_text = httshots.get_end(loses, 'Loses')
            text = httshots.strings['GamesInfoOne'].format(
                    wins, win_text, loses, lose_text)

        else:
            win_text = httshots.get_end(wins, 'Wins')
            lose_text = httshots.get_end(loses, 'Loses')
            match_text = httshots.get_end(matches, 'Matches')
            streak = httshots.streak

            text = httshots.strings['GamesInfoMore'].format(
                    matches, match_text, wins,
                    win_text, loses, lose_text)

            if streak[1] > 1:
                streak_text = httshots.strings[streak[0]][2]

                tmp = httshots.strings['GamesInfoStreak'].format(
                       streak[1], streak_text)
                text += tmp

        if url_games:
            tmp = httshots.strings['GamesInfoUrl'].format(url_games)
            text += tmp

        await ctx.send(text)

    @commands.cooldown(rate=1, per=2)
    @commands.command(aliases=("таланты", ))
    async def talents(self, ctx: commands.Context, hero: str | None = None):
        await tracker.talents(ctx, hero)
