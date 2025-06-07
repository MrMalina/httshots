# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
import asyncio

# httshots
from httshots import httshots


# ======================================================================
# >> Consts
# ======================================================================
MATCH_INFO = 1 << 0
MATCH_STATS = 1 << 1
MATCH_TALENTS = 1 << 2
MATCH_ADV_STATS = 1 << 3
MATCH_DRAFT = 1 << 4

GAMES_INFO = 1 << 0
GAMES_STREAK = 1 << 1
GAMES_URL = 1 << 2


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
        try:
            dest = httshots.cur_game[0] + '/' + httshots.cur_game[1] + '/info.log'
            httshots.visual.upload.rename_file('curgame/info.log', dest)
        except:
            ...
    else:
        # Если бот включен и уже идёт матч, либо самостоятельно добавлен реплей
        tmp = replay_name.split('/')[-1].split()
        httshots.cur_game[0] = tmp[0][2:]
        httshots.cur_game[1] = tmp[1][:-3].replace('.', '-')

    try:
        replay, protocol = httshots.parser.get_replay(replay_name)
        info = httshots.parser.get_match_info(replay, protocol)
    except:
        httshots.print_log('GameTryOpenReplay', level=2)
        await asyncio.sleep(2)
        try:
            replay, protocol = httshots.parser.get_replay(replay_name)
            info = httshots.parser.get_match_info(replay, protocol)
        except:
            httshots.print_log('GameUvi', level=2)
            return

    if httshots.config.debug:
        print(info.details.title)
        print([f'{x.name} - {x.hero}' for x in info.players.values()])

    # Игнорируем матчи, где меньше 10 игроков
    # if info == -1:
        # httshots.print_log('GameLess10Players', level=2)
        # return

    amm_id = info.init_data.game_options.amm_id
    # Свою игру игнорируем
    if amm_id == 0:
        httshots.print_log('GameUviAmmId', level=2)
        return

    # Определение пользователя в матче
    check = False
    acc_names = httshots.config.accounts
    players = {x.name:x for x in info.players.values()}
    for acc_name in acc_names:
        if acc_name in players:
            me = players[acc_name]
            check = True
            break

    if not check:
        httshots.print_log('GameNoFoundAccount', level=2)
        return

    httshots.print_log('GameAccount', me.name, level=2)

    # Находится тут, чтобы ранее вывести информацию с какого аккаунты сыгран матч
    consider_matches = httshots.config.matches_type_to_consider
    if consider_matches == 1 and amm_id != 50091:
        httshots.print_log('GameAmmIdIgnore', amm_id, level=2)
        return

    if amm_id == 50091 or consider_matches == 2:
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

    url_match = None
    url_games = None
    url_talents = None
    url_adv_stats = None
    url_draft = None

    # Вывод информации о сыгранном матче
    match_info = ""
    display_info = httshots.config.end_game_dispay_match_info
    if MATCH_INFO & display_info:
        status = httshots.strings['GameResult'+{1:'Win',2:'Lose'}[int(me.result)]]
        hero_name = httshots.htts_data.get_translate_hero(me.hero, 2)
        match_info = httshots.strings['GameResultInfo'].format(status, hero_name,
                                                               info.details.title)

    if httshots.config.image_upload:
        if MATCH_STATS & display_info:
            url_match = httshots.visual.match.create_image(info)
            if url_match:
                tmp = httshots.strings['GameResultInfoStats'].format(url_match)
                match_info += tmp

        if MATCH_TALENTS & display_info:
            url_talents = httshots.visual.talents.create_image(info)
            if url_talents:
                tmp = httshots.strings['GameResultInfoTalents'].format(url_talents)
                match_info += tmp

        if MATCH_ADV_STATS & display_info:
            url_adv_stats = httshots.visual.match_adv.create_image(info)
            if url_adv_stats:
                tmp = httshots.strings['GameResultInfoStatsAdv'].format(url_adv_stats)
                match_info += tmp

        if MATCH_DRAFT & display_info and amm_id == 50091:
            url_draft = httshots.visual.draft.create_image(info)
            if url_draft:
                tmp = httshots.strings['GameResultInfoDraft'].format(url_draft)
                match_info += tmp

    await httshots.tw_bot.channel.send(match_info)

    # Добавляем новый реплей в список сыгранных, чтобы учесть его результат
    sreplay = httshots.StreamReplay(replay_name, me, info)
    httshots.stream_replays.append(sreplay)

    # Вывод информации о сыгранном матче
    games_info = ""
    display_info = httshots.config.end_game_dispay_games_info
    if GAMES_INFO & display_info:
        wins = len(list(filter(lambda x: x.account.result == 1, httshots.stream_replays)))
        loses = len(list(filter(lambda x: x.account.result == 2, httshots.stream_replays)))
        matches = len(httshots.stream_replays)
        win_text = httshots.get_end(wins, 'Wins')
        lose_text = httshots.get_end(loses, 'Loses')
        if matches == 1:
            games_info = httshots.strings['GamesInfoOne'].format(
                wins, win_text, loses, lose_text)
        else:
            match_text = httshots.get_end(matches, 'Matches')
            games_info = httshots.strings['GamesInfoMore'].format(
                    matches, match_text, wins,
                    win_text, loses, lose_text)

            # Череда побед может быть только, когда матчей больше 1
            if GAMES_STREAK & display_info:
                streak = httshots.streak
                if streak[1] > 1:
                    streak_text = httshots.strings[streak[0]][2]
                    tmp = httshots.strings['GamesInfoStreak'].format(
                            streak[1], streak_text)
                    games_info += tmp

    if GAMES_URL & display_info and httshots.config.image_upload:
        url_games = httshots.visual.games.create_image()
        tmp = httshots.strings['GamesInfoUrl'].format(url_games)
        games_info += tmp

    await httshots.tw_bot.channel.send(games_info)

    sreplay.url_games = url_games
    sreplay.url_match = url_match
    sreplay.url_talents = url_talents
    sreplay.url_adv_stats = url_adv_stats
    sreplay.url_draft = url_draft

    httshots.bot.events.match_end(sreplay)

    httshots.print_log('SendReplayInfo', level=2)


async def check_replays():
    for acc in httshots.accounts:
        new_replay = acc.check_new_replays()
        if new_replay:
            tmp = new_replay.split('/')
            name = f".../{acc.id}/.../{tmp[-1][11:-12]}"
            httshots.print_log('NewReplay', name, level=3)
            await send_replay_info(new_replay)
            break
