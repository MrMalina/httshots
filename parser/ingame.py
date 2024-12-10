import heroprotocol
from httshots import httshots

omega_heroes = {
    'DVaPilot': 'DVa',
    'LostVikingsController': 'LostVikings'
}

def parse_content(content, pre_game):
    events = heroprotocol.versions.latest().decode_replay_tracker_events(content)

    try:
        for event in events:
            if 'm_eventName' in event and event['m_eventName'] == b'PlayerSpawned':
                index = event['m_intData'][0]['m_value']
                hero = event['m_stringData'][0]['m_value'].decode('utf8')
                hero = hero[4:]
                player = pre_game.get_player_by_index(index-1)
                player._gameloop = 0
                if hero in omega_heroes:
                    hero = omega_heroes[hero]
                player.hero = hero
                continue

            elif 'm_eventName' in event and event['m_eventName'] == b'TalentChosen':
                index = event['m_intData'][0]['m_value']
                talent = event['m_stringData'][0]['m_value'].decode('utf8')
                player = pre_game.get_player_by_index(index-1)
                player._gameloop = event['_gameloop']
                info = httshots.hero_data.get_talent_info_by_name(player.hero, talent)
                player.talents[info[1]] = info[0]
                continue

    except heroprotocol.decoders.TruncatedError:
        ...
    except Exception as e:
        print('ingame', e)
        return dict()

    heroes = {}
    for player in pre_game.players:
        if hasattr(player, 'hero'):
            heroes[player.hero] = player.talents

    return heroes