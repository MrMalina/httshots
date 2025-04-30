# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
import asyncio

# httshots
import httshots
from httshots import httshots


# ======================================================================
# >> Functions
# ======================================================================
async def send_replay_info(replay_name):
    # Close tracker task if found
    if httshots.check_talents_task is not None:
        httshots.check_talents_task.cancel()
        httshots.check_talents_task = None
        httshots.bot.tracker.old_talents = None
        httshots.visual.upload.remove_file('gametalents.png', 'curgame')
        httshots.visual.upload.remove_file('info.log', 'curgame')

    else:
        # Если бот включен и уже идёт матч, либо самостоятельно добавлен реплей
        tmp = replay_name.split('/')[-1].split()
        httshots.cur_game[0] = tmp[0][2:]
        httshots.cur_game[1] = tmp[1][:-3].replace('.', '-')

    try:
        replay, protocol = httshots.parser.get_replay(replay_name)
        info = httshots.parser.get_match_info(replay, protocol)
    except:
        httshots.print_log('GameTryOpenReplay')
        await asyncio.sleep(2)
        try:
            replay, protocol = httshots.parser.get_replay(replay_name)
            info = httshots.parser.get_match_info(replay, protocol)
        except:
            httshots.print_log('GameUvi')
            return

    if info.init_data.game_options.amm_id == 0:
        return

    check = False
    for player in info.players.values():
        if player.name in httshots.config.accounts:
            me = player
            check = True
            break
    if not check:
        httshots.print_log('GameNoFoundAccount')
        return

    httshots.print_log('GameAccount', me.name)

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
    status = httshots.strings['GameResult'+{1:'Win',2:'Lose'}[int(me.result)]]
    hero_name = httshots.htts_data.get_hero(me.hero, 1)
    # send match info

    if httshots.config.image_upload:
        url = httshots.visual.match.create_image(info)
        if url:
            url_talents = httshots.visual.talents.create_image(info)
            if httshots.config.upload_adv_stats:
                url_adv_stats = httshots.visual.match_adv.create_image(info)
                text = 'GameResultInfoWithStatsAdv'
            else:
                text = 'GameResultInfoWithStats'
                url_adv_stats = 0

        else:
            text = 'GameResultInfo'
    else:
        text = 'GameResultInfo'

    match_info = httshots.strings[text].format(status, hero_name, info.details.title,
                                               url, url_talents, url_adv_stats)
    await httshots.tw_bot.channel.send(match_info)

    # add info to stream_replays
    sreplay = httshots.StreamReplay(replay_name, me, info)
    httshots.stream_replays.append(sreplay)

    # Get url games image
    url_games = httshots.visual.games.create_image()

    sreplay.url_games = url_games
    sreplay.url_match = url
    sreplay.url_talents = url_talents
    sreplay.url_adv_stats = url_adv_stats

    # send matches info
    wins = len(list(filter(lambda x: x.account.result == 1, httshots.stream_replays)))
    loses = len(list(filter(lambda x: x.account.result == 2, httshots.stream_replays)))
    matches = len(httshots.stream_replays)
    if matches == 1:
        win_text = httshots.get_end(wins, 'Wins')
        lose_text = httshots.get_end(loses, 'Loses')
        if url_games:
            text = httshots.strings['GamesInfoOneWithStats'].format(
                    wins, win_text, loses, lose_text, url_games)
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
            text = httshots.strings['GamesInfoMoreWithStats'].format(
                    matches, match_text, wins, win_text, loses,
                    lose_text, streak[1], streak_text, url_games)
        else:
            text = httshots.strings['GamesInfoMore'].format(
                    matches, match_text, wins, win_text,
                    loses, lose_text, streak[1], streak_text)

    httshots.print_log('SendReplayInfo')

    await httshots.tw_bot.channel.send(text)


async def check_replays():
    for acc in httshots.accounts:
        new_replay = acc.check_new_replays()
        if new_replay:
            tmp = new_replay.split('/')
            name = f".../{acc.id}/.../{tmp[-1][11:-12]}"
            httshots.print_log('NewReplay', name)
            await send_replay_info(new_replay)
            break
