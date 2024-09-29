# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
# TwitchIO
from twitchio.ext import commands

# Spotipy
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# httshots
import httshots
from httshots import httshots


# ======================================================================
# >> Functions
# ======================================================================
def add_command(bot):
    command = commands.Command('song', song, aliases=("песня", ))
    bot.add_command(command)

    command = commands.Command('prevsongs', prevsongs, aliases=("песни", ))
    bot.add_command(command)

    client_id = httshots.config.spotify_client_id
    client_secret = httshots.config.spotify_client_secret
    redirect_uri = httshots.config.spotify_redirect_uri
    bot.sp_socket = spotify_get_socket(client_id, client_secret, redirect_uri)
    httshots.print_log('SpotifyReadyInfo')


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


# ======================================================================
# >> Commands
# ======================================================================
@commands.cooldown(rate=1, per=5, bucket=commands.Bucket.channel)
async def song(ctx: commands.Context):
    if ctx.bot.sp_socket:
        song = spotify_get_playing_track(ctx.bot.sp_socket)
        if song:
            text = httshots.strings['SpotifyTrack'].format(song)
        else:
            text = httshots.strings['SpotifyNoTrack']
    else:
        text = httshots.strings['SpotifyNoSocket']
    await ctx.send(text)


@commands.cooldown(rate=1, per=5, bucket=commands.Bucket.channel)
async def prevsongs(ctx: commands.Context):
    if ctx.bot.sp_socket:
        song = spotify_get_recently_tracks(ctx.bot.sp_socket, 3)
        if song:
            text = httshots.strings['SpotifyPrevTracks'].format(song)
        else:
            text = httshots.strings['SpotifyNoPrevTrack']
    else:
        text = httshots.strings['SpotifyNoSocket']
    await ctx.send(text)
