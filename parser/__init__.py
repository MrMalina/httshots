# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
import sys
import mpyq

from configobj import ConfigObj

# Others
import heroprotocol
from heroprotocol import versions

from . import classes, parse, match, battlelobby, ingame


# ======================================================================
# >> Parse
# ======================================================================
def get_replay(replay):
    # ???
    replay = mpyq.MPQArchive(replay)

    contents = replay.header['user_data_header']['content']
    header = versions.latest().decode_replay_header(contents)

    baseBuild = header['m_version']['m_baseBuild']
    try:
        protocol = versions.build(baseBuild)
    except:
        print('Unsupported base build: %d' % baseBuild, file=sys.stderr)
        return None

    return replay, protocol


def get_match_info(replay, protocol):
    contents = replay.read_file('replay.details')
    details = protocol.decode_replay_details(contents)

    game = match.Game()
    game.add_details(details)

    contents = replay.read_file('replay.initData')
    init_data = protocol.decode_replay_initdata(contents)
    game.add_init_data(init_data)

    contents = replay.header['user_data_header']['content']
    header = heroprotocol.versions.latest().decode_replay_header(contents)
    game.add_header(header)

    contents = replay.read_file('replay.tracker.events')
    info = []
    for event in protocol.decode_replay_tracker_events(contents):
        if event['_eventid'] == 11 and event['_event'] == 'NNet.Replay.Tracker.SScoreResultEvent':
            game.add_event(event['m_instanceList'])
        if (event['_eventid'] == 13 and event['_event'] == 'NNet.Replay.Tracker.SHeroBannedEvent') or (
           event['_eventid'] == 14 and event['_event'] == 'NNet.Replay.Tracker.SHeroPickedEvent'):
            info.append(event)
    game.add_lobby(info)

    return game


def get_replay_details(replay, protocol):
    contents = replay.read_file('replay.details')
    full_details = protocol.decode_replay_details(contents)

    return classes.Details(full_details)

    
def get_replay_initdata(replay, protocol):
    contents = replay.read_file('replay.initData')
    init_data = protocol.decode_replay_initdata(contents)

    return init_data


def get_replay_headers(replay):
    contents = replay.header['user_data_header']['content']
    header = latest().decode_replay_header(contents)

    return header


def get_battle_lobby(file):
    info = battlelobby.get_battle_lobby_players(file)
    pre_game = match.PreGame(info)

    return pre_game
