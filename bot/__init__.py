# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
import asyncio
import time

# twitchio
import twitchio
from twitchio.ext import commands

# httshots
import httshots
from httshots import httshots
from . import replays
from . import pregame
from . import tracker


# ======================================================================
# >> TwitchBot
# ======================================================================
class TwitchBot(commands.Bot):
    def __init__(self, token: str, prefix: str, channels: list):
        super().__init__(token=token, prefix=prefix, initial_channels=channels)

    async def event_ready(self):
        channels = self.connected_channels
        if channels:
            self.channel = channels[0]
            channel = self.channel.name
            httshots.print_log('ReadyInfo', self.nick, self.user_id, channel)
        else:
            httshots.print_log('ReadyError')
            return

        if httshots.config.add_previous_games == 1:
            found = 0
            replayes_count = 0
            for acc in httshots.accounts:
                replays = list(acc.get_replays())
                for replay_name in replays:
                    replayes_count += 1
                    replay, protocol = httshots.parser.get_replay(acc.replays_path + replay_name)
                    info = httshots.parser.get_match_info(replay, protocol)
                    if info.init_data.game_options.amm_id == 50091:
                        for player in info.players.values():
                            if player.name in httshots.config.accounts:
                                me = player
                                break

                        if me.result == 1:
                            if httshots.streak[0] == 'Wins':
                                httshots.streak[1] += 1
                            else:
                                httshots.streak[0] = 'Wins'
                                httshots.streak[1] = 1
                        else:
                            if httshots.streak[0] == 'Loses':
                                httshots.streak[1] += 1
                            else:
                                httshots.streak[0] = 'Loses'
                                httshots.streak[1] = 1

                        found = 1

                        sreplay = httshots.StreamReplay(replay_name, me, info)
                        httshots.stream_replays.append(sreplay)
                        sreplay.url_games = None
                        httshots.print_log('FoundRankedPreviousGame', replay_name[11:-12])
                    else:
                        httshots.print_log('FoundNoRankedPreviousGames', replay_name[11:-12])

            if found:
                # 2024-11-28 21.35.03 Завод Вольской -> 24-11-28 21-35
                tmp = replay_name.split()
                httshots.cur_game[0] = tmp[0][2:]
                httshots.cur_game[1] = tmp[1][:-3].replace('.', '-')

                url_games = httshots.visual.games.create_image(False)
                sreplay.url_games = url_games
                httshots.print_log('FoundPreviousGames', replayes_count, len(httshots.stream_replays))

            else:
                httshots.print_log('FoundZeroPreviousGames')

        httshots.print_log('BotStart', httshots.__name__, 
                           httshots.__author__, httshots.__version__)
        await self.endless_loop()

    async def endless_loop(self):
        while True:
            await replays.check_replays()
            await pregame.check_battle_lobby()
            await asyncio.sleep(httshots.replay_check_period)

    async def event_message(self, message: twitchio.Message):
        if hasattr(message.author, 'name'): 
            await httshots.tw_bot.handle_commands(message)
            return

    # async def event_command_error(self, ctx, error: Exception) -> None:
        # if isinstance(error, commands.CommandOnCooldown):
            # ...

    @commands.cooldown(rate=1, per=2, bucket=commands.Bucket.channel)
    @commands.command(aliases=("матч", ))
    async def game(self, ctx: commands.Context, hero: str = None, info: str = None):
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
                blue = [x.hero for x in _game.info.players.values() if x.team_id == 0]
                red = [x.hero for x in _game.info.players.values() if x.team_id == 1]
                text = httshots.strings['GameHeroes'].format(', '.join(blue), ', '.join(red))
                await ctx.send(text)
                return

            elif hero in ('счёт', 'счет', 'score'):
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

            elif hero in ('bans', 'баны'):
                bans = _game.info.lobby.bans
                for ban in bans:
                    blue_bans = ', '.join([x.hero for x in bans if x.team == 1])
                    red_bans = ', '.join([x.hero for x in bans if x.team == 2])

                text = httshots.strings['GameBans'].format(blue_bans, red_bans)
                await ctx.send(text)
                return

            player = _game.try_find_hero(hero.lower().strip())
            if player is None:
                text = httshots.strings['GameNotFoundHero'].format(ctx.author.name)
                await ctx.send(text)
                return

            if not info:
                hero = player.hero
                hero_name = httshots.hero_names.get_hero(hero, 0)
                hero_name_eng = httshots.hero_names.get_eng_hero(hero)
                talents = ''.join(map(str, player.talents))
                tmp = f" [T{talents},{hero_name_eng}]"
                icy_hero = httshots.hero_names.get_icy_hero(hero, hero_name_eng.lower())
                icy_url = httshots.icy_url.format(icy_hero, talents.replace('0', '-'))
                text = httshots.strings['GameHeroTalents'].format(hero_name, tmp, icy_url)
                await ctx.send(text)
                return

            else:
                info = info.strip().lower()
                info = httshots.data_info['params'].get(info, info)
                if info == 'score':
                    text = httshots.strings['GameHeroScore'].format(player.name, player.hero,
                                                                    player.solo_kill, player.deaths,
                                                                    player.assists)
                else:
                    value = getattr(player, info, None)
                    if value is None:
                        text = httshots.strings['GameHeroInfoNotFound'].format(info)
                    else:
                        text = httshots.strings['GameHeroInfo'].format(player.hero, info, value)
                await ctx.send(text)


    @commands.cooldown(rate=1, per=2, bucket=commands.Bucket.channel)
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
            if url_games:
                text = httshots.strings['GamesInfoOneWithStats'].format(wins, win_text, loses, lose_text, url_games)
            else:
                text = httshots.strings['GamesInfoOne'].format(wins, win_text, loses, lose_text)

        else:
            win_text = httshots.get_end(wins, 'Wins')
            lose_text = httshots.get_end(loses, 'Loses')
            match_text = httshots.get_end(matches, 'Matches')
            streak = httshots.streak
            if streak[1] == 1:
                streak_text = httshots.strings[streak[0]][1]
            else:
                streak_text = httshots.strings[streak[0]][2]
            if url_games:
                text = httshots.strings['GamesInfoMoreWithStats'].format(matches, match_text, wins,
                                                                         win_text, loses, lose_text,
                                                                         streak[1], streak_text, url_games)
            else:
                text = httshots.strings['GamesInfoMore'].format(matches, match_text, wins,
                                                                win_text, loses, lose_text,
                                                                streak[1], streak_text)


        await ctx.send(text)
