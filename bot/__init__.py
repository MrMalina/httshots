# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
import asyncio
import xlwings as xw

# Spotipy
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# twitchio
import twitchio
from twitchio.ext import commands

# httshots
import httshots
from httshots import httshots
from . import replays


match_heroes = ['герои', 'heroes']

# ======================================================================
# >> TwitchBot
# ======================================================================
class TwitchBot(commands.Bot):
    def __init__(self, token, prefix, channels):
        super().__init__(token=token, prefix=prefix, initial_channels=channels)

    async def event_ready(self):
        channels = self.connected_channels
        if channels:
            print(channels, list(self.connected_channels))
            self.channel = channels[0]
            channel = self.channel.name
            httshots.print_log('ReadyInfo', 1, self.nick, self.user_id, channel)
        else:
            httshots.print_log('ReadyError', 1)
            return

        if httshots.config['SPOTIFY_USE']:
            client_id = httshots.config['SPOTIFY_CLIENT_ID']
            client_secret = httshots.config['SPOTIFY_CLIENT_SECRET']
            redirect_uri = httshots.config['SPOTIFY_REDIRECT_URI']            
            self.sp_socket = spotify_get_socket(client_id, client_secret, redirect_uri)
            httshots.print_log('SpotifyReadyInfo', 1)
        else:
            httshots.print_log('SpotifyReadyError', 1)
            self.sp_socket = None

        httshots.print_log('BotStart', 1, httshots.__name__, 
                           httshots.__author__, httshots.__version__)
        await self.endless_loop()

    async def endless_loop(self):
        while True:
            await replays.check_replays()
            await asyncio.sleep(2)

    async def event_reconnect(self):
        httshots.print_log('BotReconnect', 1)
        if httshots.config['SPOTIFY_USE']:
            client_id = httshots.config['SPOTIFY_CLIENT_ID']
            client_secret = httshots.config['SPOTIFY_CLIENT_SECRET']
            redirect_uri = httshots.config['SPOTIFY_REDIRECT_URI']            
            self.sp_socket = spotify_get_socket(client_id, client_secret, redirect_uri)
            httshots.print_log('SpotifyReadyInfo', 1)
        else:
            httshots.print_log('SpotifyReadyError', 1)
            self.sp_socket = None

    async def event_message(self, message: twitchio.Message):
        # content = message.content
        # print(message.content)
        if hasattr(message.author, 'name'): 
            await httshots.bot.handle_commands(message)
            return

    # async def event_command_error(self, ctx, error: Exception) -> None:
        # if isinstance(error, commands.CommandOnCooldown):
            # ...

    @commands.cooldown(rate=1, per=5, bucket=commands.Bucket.channel)
    @commands.command(aliases=("песня", ))
    async def song(self, ctx: commands.Context):
        if self.sp_socket:
            song = spotify_get_playing_track(self.sp_socket)
            if song:
                text = httshots.strings['SpotifyTrack'].format(song)
            else:
                text = httshots.strings['SpotifyNoTrack']
        else:
            text = httshots.strings['SpotifyNoSocket']
        await ctx.send(text)

    @commands.cooldown(rate=1, per=5, bucket=commands.Bucket.channel)
    @commands.command()
    async def prevsongs(self, ctx: commands.Context):
        if self.sp_socket:
            song = spotify_get_recently_tracks(self.sp_socket, 3)
            if song:
                text = httshots.strings['SpotifyPrevTracks'].format(song)
            else:
                text = httshots.strings['SpotifyNoPrevTrack']
        else:
            text = httshots.strings['SpotifyNoSocket']
        await ctx.send(text)

    @commands.cooldown(rate=1, per=5, bucket=commands.Bucket.channel)
    @commands.command(aliases=("аккаунт", ))
    async def acc(self, ctx: commands.Context, name: str = None):
        if name is None:
            text = httshots.strings['AccInfoCount'].format(len(httshots.my_accounts))
            await ctx.send(text)
            return

        if name in httshots.my_accounts:
            app = xw.App(visible=False)
            book = xw.Book(httshots.excel_path)
            excel = book.sheets[0]
            for line in range(2, 100):
                if excel['A%s'%line].value == name:
                    rank = excel['B%s'%line].value
                    tmp = httshots.strings['Rank%s'%rank[0]] + rank[1:]
                    text = httshots.strings['AccInfoRank'].format(name, tmp, httshots.my_accounts[name])
                    book.close()
                    app.quit()
                    await ctx.send(text)
                    return

            text = httshots.strings['AccInfo'].format(name, httshots.my_accounts[name])
            await ctx.send(text)
        else:
            text = httshots.strings['AccInfoNone'].format(ctx.author.name)
            await ctx.send(text)


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
            if hero in match_heroes:
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

            if info is None:
                hero_name = httshots.heroes['heroes_ru'].get(player.hero, [0,0,0,0,0])[0]
                hero_name_eng = httshots.heroes['heroes_en'].get(player.hero, None)
                talents = ''.join(map(str, player.talents))
                tmp = f" [T{talents},{hero_name_eng}]"
                icy_hero = httshots.heroes['heroes_icy'].get(hero_name, hero_name_eng.lower())
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
        wins = len(list(filter(lambda x: x.account.result == 1, httshots.stream_replays)))
        loses = len(list(filter(lambda x: x.account.result == 2, httshots.stream_replays)))
        matches = len(httshots.stream_replays)
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


# ======================================================================
# >> Functions
# ======================================================================
def spotify_get_socket(client_id, client_secret, redirect_uri):
    scope = "user-read-currently-playing user-read-private user-read-recently-played"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,
                         client_id=client_id,
                         client_secret=client_secret,
                         redirect_uri=redirect_uri,
                         cache_path=httshots.current_dir + "\\files\\cache"))
    return sp


def spotify_get_playing_track(sp):
    track_info = sp.current_user_playing_track()
    if track_info is not None:
        item = track_info['item']
        track_name = item['name']
        artists = []
        for art in item['artists']:
            artists.append(art['name'])
        return f"{', '.join(artists)} - {track_name}"
    return None


def spotify_get_recently_tracks(sp, count):
    tracks = sp.current_user_recently_played(count)
    if tracks is not None:
        info = []
        for number, track in enumerate(tracks['items']):
            track_info = track['track']
            track_name = track_info['name']
            artists = []
            for art in track_info['artists']:
                artists.append(art['name'])
            info.append(f"{number+1}. {', '.join(artists)} - {track_name}")
        return '  '.join(info)
    return None

