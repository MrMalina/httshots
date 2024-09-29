import httshots

from httshots import httshots

from . import match
from . import games
from . import talents
from . import battlelobby

mvps = {
    'mvp':'mvp',
    'xp': 'experienced',
    'escapes': 'escapeartist',
    'zerg': 'zergcrusher',
    'roots': 'trapper',
    'temple': 'templemaster',
    'skulls': 'skull',
    'gems': 'jeweler',
    'daredevil_escapes': 'daredevil',
    'vengeances': 'avenger',
    'immortal': 'immortalslayer',
    'curse': 'masterofthecurse',
    'dragon': 'shriner',
    'healing': 'mainhealer',
    'silences': 'silencer',
    'stuns': 'stunner',
    'pushing': 'pusher',
    'outnumbered_deaths': 'solesurvivor',
    'hat_trick': 'hattrick',
    'shields': 'protector',
    'siege_damage': 'siegemaster',
    'altar': 'cannoneer',
    'clutch_healing': 'clutchhealer',
    'teamfight_healing': 'combatmedic',
    'hero_damage': 'painbringer',
    'time_on_point': 'pointguard',
    'outnumbered_deaths': 'teamplayer',
    'cage_unlocks': 'wcav',
    'taken_damage': 'bulwark',
    'teamfight_taken_damage': 'guardian',
    'teamfight_hero_damage': 'scrapper',
    'mercs': 'headhunter',
    'kill_streak': 'finisher',
    'seeds': 'gardenterror',
}


def upload_image(file_name):
    upl = httshots.config.image_upload
    if not upl:
        return None

    elif upl == 1:
        url = upload_image_imgur(file_name)
        if url is None and httshots.config.try_reupload_image:
            url = upload_image_imgur(file_name)

    return url


def upload_image_imgur(file_name):
    try:
        url = httshots.imgur.upload_from_path(file_name)
        if 'link' in url:
            return url['link'].replace('i.', '')
        return None
    except Exception as e:
        print(e)
        return None
