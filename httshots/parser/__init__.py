# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
import sys
import mpyq

from collections import defaultdict

# Others
import heroprotocol
from heroprotocol import versions

# httshots
from httshots import httshots
from . import classes, parse, match, battlelobby, ingame, units


# ======================================================================
# >> Parse
# ======================================================================
def get_replay(replay):
    replay = mpyq.MPQArchive(replay)

    contents = replay.header['user_data_header']['content']
    header = versions.latest().decode_replay_header(contents)

    base_build = header['m_version']['m_baseBuild']

    try:
        protocol = versions.build(base_build)
    except:
        if base_build < int(httshots.HOTS_VERSION):
            httshots.print_log('BotHeroprotocolBuildOld', base_build, level=5)
        elif base_build > int(httshots.HOTS_VERSION):
            httshots.print_log('BotHeroprotocolBuildNew', base_build, level=5)
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

    # messages = []
    # contents = replay.read_file('replay.message.events')
    # for event in decode_replay_message_events(contents):
        # print(event)

    # game.add_init_data(init_data)

    contents = replay.read_file('replay.tracker.events')
    info = []
    game_loops = defaultdict(list)
    game_units = {}
    hero_units = {}
    for event in protocol.decode_replay_tracker_events(contents):
        if event['_eventid'] == 11 and event['_event'] == 'NNet.Replay.Tracker.SScoreResultEvent':
            game.add_event(event['m_instanceList'])
        elif event['_event'] == 'NNet.Replay.Tracker.SPlayerSetupEvent':
            game.add_user_id(event['m_userId'])
        elif (event['_eventid'] == 13 and
            event['_event'] == 'NNet.Replay.Tracker.SHeroBannedEvent') or \
            (event['_eventid'] == 14 and
            event['_event'] == 'NNet.Replay.Tracker.SHeroPickedEvent'):
            info.append(event)
        elif event['_event'] == 'NNet.Replay.Tracker.SUnitBornEvent':
            unit = units.GameUnit(event)
            game_units[unit.tag] = unit
        elif event['_event'] == 'NNet.Replay.Tracker.SUnitDiedEvent':
            tag = units.get_unit_tag(event)
            game_units[tag].unit_dead(event)
        elif event['_event'] == 'NNet.Replay.Tracker.SStatGameEvent':
            if event['m_eventName'] == b'PlayerSpawned':
                hero = units.HeroUnit(event)
                hero_units[hero.player_id] = hero
            elif event['m_eventName'] == b'PlayerDeath':
                player_id = units.get_hero_unit(event)
                hero = hero_units[player_id]
                hero.add_death(event)

    game.game_units = game_units
    game.hero_units = hero_units
    game.add_lobby(info)

    for unit in game_units.values():
        game_loops[unit.born_gameloop].append(('SpawnUnit', unit))
        game_loops[unit.dead_gameloop].append(('DeathUnit', unit))

    for hero in hero_units.values():
        for death in hero.deaths:
            game_loops[death.gameloop].append(('DeathHero', hero))

    game.game_loops = game_loops

    # hero_level
    # contents = replay.read_file('replay.attributes.events')
    # attributes = protocol.decode_replay_attributes_events(contents)
    # for player_id in attributes['scopes'].keys():
        # if player_id > 10: continue
        # print(player_id)
        # print(attributes['scopes'][player_id][500][0]['value'])
        # if attributes['scopes'][player_id][500][0]['value'] == b'Humn':
            # lvl = attributes['scopes'][player_id][4008][0]['value']
            # game.players[int(player_id)-1].hero_level = int(lvl.decode().strip())

    return game


def get_battle_lobby(file):
    info = battlelobby.get_battle_lobby_players(file)
    pre_game = match.PreGame(info)

    return pre_game
