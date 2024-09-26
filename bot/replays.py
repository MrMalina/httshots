# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
import asyncio
import hashlib
import os

# httshots
import httshots
from httshots import httshots


# ======================================================================
# >> Functions
# ======================================================================
async def send_replay_info(replay_name):
    language = httshots.language

    try:
        replay, protocol = httshots.parser.get_replay(replay_name)
        info = httshots.parser.get_match_info(replay, protocol)
    except:
        httshots.print_log('GameTryOpenReplay', 1)
        await asyncio.sleep(2)
        try:
            replay, protocol = httshots.parser.get_replay(replay_name)
            info = httshots.parser.get_match_info(replay, protocol)
        except:
            httshots.print_log('GameUvi', 1)
            return

    if info.init_data.game_options.amm_id == 0:
        return

    check = False
    for player in info.players.values():
        if player.name in httshots.config['ACCOUNTS']:
            me = player
            check = True
            break
    if not check:
        httshots.print_log('GameNoFoundAccount', 3)
        return

    # streak
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

    # get hero_name
    status = httshots.strings['GameResult%s'%{1:'Win',2:'Lose'}[int(me.result)]]
    hero_name = httshots.data_heroes['names'].get(me.hero, None)[2]
    if hero_name is None:
        for hero_name in httshots.data_heroes['names']:
            if hero_name.startswith(me.hero):
                break
    # send match info

    if httshots.imgur is not None:
        url = httshots.score.match.create_image(info)
        if url:
            text = 'GameResultInfoWithStats'
        else:
            text = 'GameResultInfo'
        url_talents = httshots.score.talents.create_image(info)
    else:
        text = 'GameResultInfo'

    match_info = httshots.strings[text].format(status, hero_name, info.details.title, url, url_talents)
    await httshots.bot.channel.send(match_info)

    # add info to stream_replays
    sreplay = httshots.StreamReplay(replay_name, me, info)
    httshots.stream_replays.append(sreplay)

    # Get url games image
    url_games = httshots.score.games.create_image()

    sreplay.url_games = url_games
    sreplay.url_match = url
    sreplay.url_talents = url_talents

    # send matches info
    wins = len(list(filter(lambda x: x.account.result == 1, httshots.stream_replays)))
    loses = len(list(filter(lambda x: x.account.result == 2, httshots.stream_replays)))
    matches = len(httshots.stream_replays)
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

    httshots.print_log('SendReplayInfo', 3)

    await httshots.bot.channel.send(text)


async def send_battle_lobby_info(info):
    url = httshots.score.battlelobby.create_image(info)
    text = httshots.strings['LobbyInfo'].format(url)
    await httshots.bot.channel.send(text)


async def check_replays():
    for acc in httshots.accounts:
        # new_replay = acc.replays_path + list(acc.get_replays())[0]
        new_replay = acc.check_new_replays()
        if new_replay:
            httshots.print_log('NewReplay', 3, new_replay, acc.id)
            await send_replay_info(new_replay)
            break


async def check_battle_lobby():
    try:
        if os.path.isfile(httshots.battle_lobby_file):
            file = open(httshots.battle_lobby_file, 'rb')
            contents = file.read()
            file.close()
            hash = hashlib.md5(contents).hexdigest()
            if httshots.battle_lobby_hash is None or httshots.battle_lobby_hash != hash:
                httshots.battle_lobby_hash = hash
                info = httshots.parser.get_battle_lobby(contents)
                await send_battle_lobby_info(info)
    except Exception as e:
        print('Oooooops', e)
