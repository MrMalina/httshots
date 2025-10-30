# ======================================================================
# >> IMPORTS
# ======================================================================

# httshots
from httshots import httshots


# ======================================================================
# >> Functions
# ======================================================================
def update_score(clear_score=0):
    if not clear_score:
        if httshots.config.score_game_type == 2:
            wins = len(list(filter(lambda x: x.account.result == 1, httshots.stream_replays)))
            loses = len(list(filter(lambda x: x.account.result == 2, httshots.stream_replays)))
        else:
            wins = len(list(filter(lambda x: x.account.result == 1 and x.info.game_type == 50091,
                        httshots.stream_replays)))
            loses = len(list(filter(lambda x: x.account.result == 2 and x.info.game_type == 50091,
                         httshots.stream_replays)))
    else:
        wins = 0
        loses = 0

    score_string = httshots.strings['ScoreStringType%s'%httshots.config.score_string_type]
    if httshots.config.score_colors:
        win_color = '69f969'
        lose_color = 'ea8c8c'
    else:
        win_color = 'ffffff'
        lose_color = 'ffffff'
    score_string = score_string.format(win_color=win_color,lose_color=lose_color,
                                       wins=wins,loses=loses)

    streak = ""
    if httshots.config.score_streak:
        games = httshots.streak[1]
        if games:
            streak = httshots.strings['ScoreStringStreak']
            if httshots.streak[0] == 'Loses':
                color = lose_color
                text = httshots.strings['Loses'][2]
            else:
                color = win_color
                text = httshots.strings['Wins'][2]
            streak = streak.format(color, text, games) + '<br>'

    with open(httshots.paths.upload / 'score_sample.html', 'r') as f:
        text = f.readlines()
        text[20] = score_string + '<br>' + streak

    with open(httshots.paths.upload / 'score.html', 'w', encoding='ansi') as f:
        for line in text:
            f.write(line)
