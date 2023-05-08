# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
from configobj import ConfigObj
import mpyq

# Others
import heroprotocol
from heroprotocol import versions

from . import classes, parse, match


# ======================================================================
# >> Parse
# ======================================================================
def get_replay(replay):
    # ???
    replay = mpyq.MPQArchive(replay)

    contents = replay.header['user_data_header']['content']
    header = heroprotocol.versions.latest().decode_replay_header(contents)

    baseBuild = header['m_version']['m_baseBuild']
    try:
        protocol = heroprotocol.versions.build(baseBuild)
    except:
        print('Unsupported base build: %d' % baseBuild, file=sys.stderr)
        return None

    return replay, protocol


def get_match_info(replay, protocol):
    contents = replay.read_file('replay.details')
    details = protocol.decode_replay_details(contents)

    game = match.Match()
    game.add_details(details)

    contents = replay.read_file('replay.initData')
    init_data = protocol.decode_replay_initdata(contents)
    game.add_init_data(init_data)

    contents = replay.header['user_data_header']['content']
    header = heroprotocol.versions.latest().decode_replay_header(contents)
    game.add_header(header)

    return game


def get_replay_details(replay, protocol):
    contents = replay.read_file('replay.details')
    full_details = protocol.decode_replay_details(contents)

    return details.Details(full_details)

    
def get_replay_initdata(replay, protocol):
    contents = replay.read_file('replay.initData')
    init_data = protocol.decode_replay_initdata(contents)

    return init_data


def get_replay_headers(replay):
    contents = replay.header['user_data_header']['content']
    header = versions.latest().decode_replay_header(contents)

    return header
