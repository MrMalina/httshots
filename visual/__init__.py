# ======================================================================
# >> IMPORTS
# ======================================================================
# python
import re
from PIL import Image

# httshots
from . import draft
from . import match
from . import match_adv
from . import games
from . import talents
from . import battlelobby
from . import tracker
from . import upload


# ======================================================================
# >> CONSTS
# ======================================================================
check_name = re.compile("[a-zA-Zа-яА-Я0-9]*")


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


# ======================================================================
# >> Functions
# ======================================================================
def create_board(border_path):
    vborder = Image.open(border_path+'verticalborder.png')
    vborder_size = vborder.size
    bghex = Image.open(border_path+'backgroundhex.png')
    bghex_size = bghex.size
    hborder = Image.open(border_path+'horizontalborder_bottom.png')
    hborder_size = hborder.size

    image = Image.new('RGBA', (bghex_size[0]+vborder_size[0]-2, vborder_size[1]+hborder_size[1]))

    bg = Image.open(border_path+'background.png')
    bg = bg.resize((bghex_size[0]+vborder_size[0]-2, vborder_size[1]+hborder_size[1]-5))
    image.paste(bg, (0, 0))

    image.paste(bghex, (0, 0), mask=bghex)

    image.paste(vborder, (0, 0), mask=vborder)

    image.paste(hborder, (0, vborder_size[1]), mask=hborder)

    bborder = Image.open(border_path+'bottomborder.png')
    bborder_size = bborder.size
    image.paste(bborder, (hborder_size[0], vborder_size[1]+hborder_size[1]-23), mask=bborder)

    bborderright = Image.open(border_path+'horizontalborder_bottom_right.png')
    image.paste(bborderright, (hborder_size[0]+bborder_size[0], vborder_size[1]), mask=bborderright)

    vborderright = Image.open(border_path+'verticalborder_right.png')
    image.paste(vborderright, (bghex_size[0]-2, 0), mask=vborderright)

    hborder = Image.open(border_path+'horizontalborder.png')
    hborder_size = hborder.size
    image.paste(hborder, (20, 0), mask=hborder)

    return image
