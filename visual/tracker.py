# ======================================================================
# >> IMPORTS
# ======================================================================

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import httshots
from httshots import httshots


# ======================================================================
# >> CONFIGS
# ======================================================================
path = r"d:\games\python\httshots\files/"
bg_files = path + "background/"
score_files = path + "scorescreen/"
font_files = path + "ttf/"
screens_files = path + "screens/"
stats_files = path + "stats/"
talents_files = path + "talents/"
font = ImageFont.truetype(font_files+'Exo2-Bold.ttf', 16)
large_font = ImageFont.truetype(font_files+'Exo2-Bold.ttf', 24)
big_font = ImageFont.truetype(font_files+'Exo2-Bold.ttf', 46)


# ======================================================================
# >> FUNCTIONS
# ======================================================================
def create_board():
    border_files = path + "border/"
    vborder = Image.open(border_files+'verticalborder.png')
    vborder_size = vborder.size
    bghex = Image.open(border_files+'backgroundhex.png')
    bghex_size = bghex.size
    hborder = Image.open(border_files+'horizontalborder_bottom.png')
    hborder_size = hborder.size

    image = Image.new('RGBA', (bghex_size[0]+vborder_size[0]-2, vborder_size[1]+hborder_size[1]))

    bg = Image.open(border_files+'background.png')
    bg = bg.resize((bghex_size[0]+vborder_size[0]-2, vborder_size[1]+hborder_size[1]-5))
    image.paste(bg, (0, 0))

    image.paste(bghex, (0, 0), mask=bghex)

    image.paste(vborder, (0, 0), mask=vborder)

    image.paste(hborder, (0, vborder_size[1]), mask=hborder)

    bborder = Image.open(border_files+'bottomborder.png')
    bborder_size = bborder.size
    image.paste(bborder, (hborder_size[0], vborder_size[1]+hborder_size[1]-23), mask=bborder)

    bborderright = Image.open(border_files+'horizontalborder_bottom_right.png')
    bborderright_size = bborderright.size
    image.paste(bborderright, (hborder_size[0]+bborder_size[0], vborder_size[1]), mask=bborderright)

    vborderright = Image.open(border_files+'verticalborder_right.png')
    vborderright_size = vborderright.size
    image.paste(vborderright, (bghex_size[0]-2, 0), mask=vborderright)

    hborder = Image.open(border_files+'horizontalborder.png')
    hborder_size = hborder.size
    image.paste(hborder, (20, 0), mask=hborder)

    return image


def create_icons(image):
    draw = ImageDraw.Draw(image)
    draw.text((495, 50), "1", (255,255,255), font=large_font)
    draw.text((595, 50), "4", (255,255,255), font=large_font)
    draw.text((695, 50), "7", (255,255,255), font=large_font)
    draw.text((790, 50), "10", (255,255,255), font=large_font)
    draw.text((890, 50), "13", (255,255,255), font=large_font)
    draw.text((990, 50), "16", (255,255,255), font=large_font)
    draw.text((1090, 50), "20", (255,255,255), font=large_font)



def add_heroes(image, players):
    heroes_files = path + "heroes/"

    blue = Image.open(score_files+'blue.png')
    bplayer = Image.open(score_files+'playerblue.png').convert('RGBA')
    red = Image.open(score_files+'red.png')
    rplayer = Image.open(score_files+'playerred.png').convert('RGBA')
    glow = Image.open(score_files+'portrait.png').convert('RGBA')
    language = httshots.language

    talent_available = Image.open(talents_files+'talent_available.png')
    talent_available_ult = Image.open(talents_files+'talent_available_ult.png')
    talent_bg = Image.open(talents_files+'talent_bg.png')
    talent_unavailable = Image.open(talents_files+'talent_unavailable.png')
    talent_unselected = Image.open(talents_files+'talent_unselected.png')

    add = 100
    rng = 60

    _gameloop = 0
    for x, player in enumerate(players):
        hero_name = httshots.hero_names.get_data_revers_name(player.hero)
        # hero_name = httshots.hero_names.get_eng_hero(hero_name)
        hero = Image.open(heroes_files+hero_name.lower()+'.png').convert('RGBA')

        draw = ImageDraw.Draw(image)
        team_id = player.userid > 4

        if team_id == 0:
            image.paste(bplayer, (25, add+(x*rng)), mask=bplayer)
            image.paste(blue, (25+rplayer.size[0], add+(x*rng)), mask=blue)
            image.paste(hero, (40, add+(x*rng)), mask=glow)
            draw.text((155, add+(x*rng)+30), player.battle_tag, (105,156,249), font=font)
            color = (105,156,249)
            postfix = 'blue'

        else:
            image.paste(rplayer, (25, add+(x*rng)), mask=rplayer)
            image.paste(red, (25+rplayer.size[0], add+(x*rng)), mask=red)
            image.paste(hero, (40, add+(x*rng)), mask=glow)
            draw.text((155, add+(x*rng)+30), player.battle_tag, (234,140,140), font=font)
            color = (234,140,140)
            postfix = 'red'

        hero_short_name = httshots.hero_names.get_short_hero(player.hero)
        draw.text((155, add+(x*rng)+10), hero_short_name, (255,255,255), font=font)

        # team_level = player.team_level

        data_hero_name = httshots.hero_names.get_data_name(hero_name)
        info = httshots.hero_data[data_hero_name]['talents']
        talents = player.talents
        start = 500 - 30
        for z in zip([1, 4, 7, 10, 13, 16, 20], talents):
            level = z[0]
            talent = z[1]
            # if level <= team_level:
            if talent == 0:
                image.paste(talent_unselected, (start+13, add+(x*rng+7)), mask=talent_unselected)
            else:
                icon = info['level%s'%level][talent-1]['icon']
                icon = Image.open(talents_files+icon)
                icon = icon.resize((46, 46))
                image.paste(icon, (start+11, add+(x*rng+6)))

            # else:
                # image.paste(talent_bg, (start+11, add+(x*rng+6)), mask=talent_bg)
                # image.paste(talent_unavailable, (start, add+(x*rng-6)), mask=talent_unavailable)
                # start += 100
                # continue

            if level != 10:
                image.paste(talent_available, (start, add+(x*rng-6)), mask=talent_available)
            else:
                image.paste(talent_available_ult, (start, add+(x*rng - 6)), mask=talent_available_ult)

            start += 100

        if player._gameloop > _gameloop:
            _gameloop = player._gameloop

    if language == 'RU':
        coords = (555, 720)
    else:
        coords = (580, 720)

    _time = int((_gameloop - 610) / 16)
    draw.text(coords, httshots.strings['ImageMatchDuration'], (138,166,251), font=large_font)
    draw.text((610, 745), f"{_time//60}:{_time%60}", (255, 255, 255), font=big_font)




def create_image(players):
    httshots.print_log('ImgurStartCreateTalentsImage')
    httshots.print_log('ImgurCreateBorder')
    image = create_board()

    httshots.print_log('ImgurCreateIcons')
    create_icons(image)

    httshots.print_log('ImgurAddHeroes')
    add_heroes(image, players)

    httshots.print_log('ImgurSaveImageMatch')
    image.save(screens_files + 'gametalents.png')

    httshots.print_log('ImgurUploadImageMatch')
    _name = 'gametalents.png'
    url = httshots.visual.upload.upload_image(screens_files + _name,
                                 _name, True, 'curgame')

    return url
