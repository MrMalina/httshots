# ======================================================================
# >> IMPORTS
# ======================================================================

from PIL import Image
from PIL import ImageDraw

import httshots
from httshots import httshots as hots


# ======================================================================
# >> FUNCTIONS
# ======================================================================
def create_board():
    border_path = hots.config.vs_border_path

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


def create_icons(image):
    draw = ImageDraw.Draw(image)
    draw.text((495, 50), "1", (255,255,255), font=hots.config.vs_large_font)
    draw.text((595, 50), "4", (255,255,255), font=hots.config.vs_large_font)
    draw.text((695, 50), "7", (255,255,255), font=hots.config.vs_large_font)
    draw.text((790, 50), "10", (255,255,255), font=hots.config.vs_large_font)
    draw.text((890, 50), "13", (255,255,255), font=hots.config.vs_large_font)
    draw.text((990, 50), "16", (255,255,255), font=hots.config.vs_large_font)
    draw.text((1090, 50), "20", (255,255,255), font=hots.config.vs_large_font)



def add_heroes(image, replay):
    score_path = hots.config.vs_score_path
    talents_path = hots.config.vs_talents_path

    blue = Image.open(score_path+'blue.png')
    bplayer = Image.open(score_path+'playerblue.png').convert('RGBA')
    red = Image.open(score_path+'red.png')
    rplayer = Image.open(score_path+'playerred.png').convert('RGBA')
    glow = Image.open(score_path+'portrait.png').convert('RGBA')

    talent_available = Image.open(talents_path+'talent_available.png')
    talent_available_ult = Image.open(talents_path+'talent_available_ult.png')
    talent_bg = Image.open(talents_path+'talent_bg.png')
    talent_unavailable = Image.open(talents_path+'talent_unavailable.png')
    talent_unselected = Image.open(talents_path+'talent_unselected.png')

    add = 100
    rng = 60

    for x, player in enumerate(replay.players.values()):
        hero_name = hots.hero_names.get_eng_hero(player.hero)
        hero = Image.open(hots.config.vs_heroes_path+hero_name.lower()+'.png').convert('RGBA')

        draw = ImageDraw.Draw(image)

        team_id = player.team_id

        if team_id == 0:
            image.paste(bplayer, (25, add+(x*rng)), mask=bplayer)
            image.paste(blue, (25+rplayer.size[0], add+(x*rng)), mask=blue)
            image.paste(hero, (40, add+(x*rng)), mask=glow)
            draw.text((155, add+(x*rng)+30), player.name, (105,156,249), font=hots.config.vs_font)

        else:
            image.paste(rplayer, (25, add+(x*rng)), mask=rplayer)
            image.paste(red, (25+rplayer.size[0], add+(x*rng)), mask=red)
            image.paste(hero, (40, add+(x*rng)), mask=glow)
            draw.text((155, add+(x*rng)+30), player.name, (234,140,140), font=hots.config.vs_font)

        hero_short_name = hots.hero_names.get_short_hero(player.hero)
        draw.text((155, add+(x*rng)+10), hero_short_name, (255,255,255), font=hots.config.vs_font)

        team_level = player.team_level

        data_hero_name = hots.hero_names.get_data_name(hero_name)
        info = hots.hero_data[data_hero_name]['talents']
        talents = player.talents
        start = 500 - 30
        for z in zip([1, 4, 7, 10, 13, 16, 20], talents):
            level = z[0]
            talent = z[1]
            if level <= team_level:
                if talent == 0:
                    image.paste(talent_unselected, (start+13, add+(x*rng+7)), mask=talent_unselected)
                else:
                    icon = info['level%s'%level][talent-1]['icon']
                    icon = Image.open(talents_path+icon)
                    icon = icon.resize((46, 46))
                    image.paste(icon, (start+11, add+(x*rng+6)))

            else:
                image.paste(talent_bg, (start+11, add+(x*rng+6)), mask=talent_bg)
                image.paste(talent_unavailable, (start, add+(x*rng-6)), mask=talent_unavailable)
                start += 100
                continue

            if data_hero_name != 'Varian':
                if level != 10:
                    image.paste(talent_available, (start, add+(x*rng-6)), mask=talent_available)
                else:
                    image.paste(talent_available_ult, (start, add+(x*rng - 6)), mask=talent_available_ult)
            else:
                if level != 4:
                    image.paste(talent_available, (start, add+(x*rng-6)), mask=talent_available)
                else:
                    image.paste(talent_available_ult, (start, add+(x*rng - 6)), mask=talent_available_ult)

            start += 100


def add_other_info(image, replay):
    language = hots.language

    red_kills = 0
    blue_kills = 0
    for player in replay.players.values():
        if player.team_id == 0:
            blue_level = player.team_level
        else:
            red_level = player.team_level

    player = list(replay.players.values())[0]
    time = player.time

    draw = ImageDraw.Draw(image)
    if language == 'ru':
        coords = (80, 710)
    else:
        coords = (105, 710)

    draw.text(coords, hots.strings['ImageBlueTeam'], (185,213,255), font=hots.config.vs_large_font)
    draw.text((105, 740), hots.strings('ImageLevelTeam', blue_level), (39,153,165), font=hots.config.vs_large_font)

    draw.text((1350-250, 710), hots.strings['ImageRedTeam'], (234,140,140), font=hots.config.vs_large_font)
    draw.text((1350-250, 740), hots.strings('ImageLevelTeam', red_level), (175,76,105), font=hots.config.vs_large_font)

    draw.text((550, 720), hots.strings['ImageMatchDuration'], (138,166,251), font=hots.config.vs_large_font)
    draw.text((610, 745), f"{str(time//60).zfill(2)}:{str(time%60).zfill(2)}", (255, 255, 255), font=hots.config.vs_big_font)

    if player.result == 1:
        if player.team_id == 0:
            text = hots.strings['ImageBlueWin']
            color = (39,153,165)
        else:
            text = hots.strings['ImageRedWin']
            color = (175,76,105)
    else:
        if player.team_id == 0:
            text = hots.strings['ImageRedWin']
            color = (175,76,105)
        else:
            text = hots.strings['ImageBlueWin']
            color = (39,153,165)

    draw.text((40, 50), text, color, font=hots.config.vs_large_font)


def create_image(replay):
    _name = 'talents.png'
    hots.print_log('ImageStartCreateTalentsImage', uwaga=0)
    hots.print_log('ImageCreateBorder', uwaga=0)
    image = create_board()

    hots.print_log('ImageCreateIcons', uwaga=0)
    create_icons(image)

    hots.print_log('ImageAddHeroes', uwaga=0)
    add_heroes(image, replay)

    hots.print_log('ImageAddOtherInfo', uwaga=0)
    add_other_info(image, replay)

    hots.print_log('ImageSaveImageMatch', uwaga=0)
    image.save(hots.config.vs_screens_path + _name)

    hots.print_log('ImageUploadTalents')
    url = hots.visual.upload.upload_file(hots.config.vs_screens_path + _name, _name)

    return url
