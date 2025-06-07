# ======================================================================
# >> IMPORTS
# ======================================================================

from PIL import Image
from PIL import ImageDraw

import httshots
from httshots import httshots as hots


# ======================================================================
# >> CONSTS
# ======================================================================
WHITE = (255,255,255)
BTEAM = (105,156,249)
RTEAM = (234,140,140)


# ======================================================================
# >> FUNCTIONS
# ======================================================================
def load_background():
    return Image.open(hots.paths.bg / 'games_background.png')


def create_icons(image):
    draw = ImageDraw.Draw(image)
    draw.text((495, 50), "1", WHITE, font=hots.fonts.large)
    draw.text((595, 50), "4", WHITE, font=hots.fonts.large)
    draw.text((695, 50), "7", WHITE, font=hots.fonts.large)
    draw.text((790, 50), "10", WHITE, font=hots.fonts.large)
    draw.text((890, 50), "13", WHITE, font=hots.fonts.large)
    draw.text((990, 50), "16", WHITE, font=hots.fonts.large)
    draw.text((1090, 50), "20", WHITE, font=hots.fonts.large)


def add_heroes(image, replay):
    blue = Image.open(hots.paths.utils / 'blue.png')
    bplayer = Image.open(hots.paths.utils / 'playerblue.png').convert('RGBA')
    red = Image.open(hots.paths.utils / 'red.png')
    rplayer = Image.open(hots.paths.utils / 'playerred.png').convert('RGBA')
    glow = Image.open(hots.paths.utils / 'portrait.png').convert('RGBA')

    t_available = Image.open(hots.paths.talents / 'talent_available.png')
    t_available_ult = Image.open(hots.paths.talents / 'talent_available_ult.png')
    t_bg = Image.open(hots.paths.talents / 'talent_bg.png')
    t_unavailable = Image.open(hots.paths.talents / 'talent_unavailable.png')
    t_unselected = Image.open(hots.paths.talents / 'talent_unselected.png')

    add = 100
    rng = 60

    for x, player in enumerate(replay.players.values()):
        hero_name = player.hero
        img_name = hots.htts_data.remove_symbols(hero_name)
        img_name = 'portrait_' + img_name + '.png'
        hero = Image.open(hots.paths.heroes / img_name).convert('RGBA')

        draw = ImageDraw.Draw(image)

        team_id = player.team_id

        name = player.name
        check = hots.visual.check_name.match(name)[0]
        if check:
            name_font = hots.fonts.default
        else:
            name_font = hots.fonts.ch_default

        if team_id == 0:
            image.paste(bplayer, (25, add+(x*rng)), mask=bplayer)
            image.paste(blue, (25+rplayer.size[0], add+(x*rng)), mask=blue)
            image.paste(hero, (40, add+(x*rng)), mask=glow)
            draw.text((155, add+(x*rng)+30), name, BTEAM, font=name_font)

        else:
            image.paste(rplayer, (25, add+(x*rng)), mask=rplayer)
            image.paste(red, (25+rplayer.size[0], add+(x*rng)), mask=red)
            image.paste(hero, (40, add+(x*rng)), mask=glow)
            draw.text((155, add+(x*rng)+30), name, RTEAM, font=name_font)

        tr_hero_name = hots.htts_data.get_translate_hero(player.hero, 0)
        hero_short_name = hots.htts_data.get_short_hero(tr_hero_name)
        draw.text((155, add+(x*rng)+10), hero_short_name, WHITE, font=hots.fonts.default)

        team_level = player.team_level

        data_hero_name = hots.htts_data.get_data_name(hero_name)
        info = hots.hero_data[data_hero_name]['talents']
        talents = player.talents
        start = 500 - 30
        for z in zip([1, 4, 7, 10, 13, 16, 20], talents):
            level = z[0]
            talent = z[1]
            if level <= team_level:
                if talent == 0:
                    image.paste(t_unselected, (start+13, add+(x*rng+7)), mask=t_unselected)
                else:
                    icon = info['level'+str(level)][talent-1]['icon']
                    icon = Image.open(hots.paths.talents /icon)
                    icon = icon.resize((46, 46))
                    image.paste(icon, (start+11, add+(x*rng+6)))

            else:
                image.paste(t_bg, (start+11, add+(x*rng+6)), mask=t_bg)
                image.paste(t_unavailable, (start, add+(x*rng-6)), mask=t_unavailable)
                start += 100
                continue

            if data_hero_name != 'Varian':
                if level != 10:
                    image.paste(t_available, (start, add+(x*rng-6)), mask=t_available)
                else:
                    image.paste(t_available_ult, (start, add+(x*rng - 6)), mask=t_available_ult)
            else:
                if level != 4:
                    image.paste(t_available, (start, add+(x*rng-6)), mask=t_available)
                else:
                    image.paste(t_available_ult, (start, add+(x*rng - 6)), mask=t_available_ult)

            start += 100


def add_other_info(image, replay):
    language = hots.config.language

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

    tmp = hots.strings('ImageLevelTeam', blue_level)
    draw.text(coords, hots.strings['ImageBlueTeam'], (185,213,255), font=hots.fonts.large)
    draw.text((105, 740), tmp, (39,153,165), font=hots.fonts.large)

    tmp = hots.strings('ImageLevelTeam', red_level)
    draw.text((1350-250, 710), hots.strings['ImageRedTeam'], (234,140,140), font=hots.fonts.large)
    draw.text((1350-250, 740), tmp, (175,76,105), font=hots.fonts.large)

    draw.text((550, 720), hots.strings['ImageMatchDuration'], (138,166,251), font=hots.fonts.large)
    tmp = f"{str(time//60).zfill(2)}:{str(time%60).zfill(2)}"
    draw.text((610, 745), tmp, WHITE, font=hots.fonts.big)

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

    draw.text((40, 50), text, color, font=hots.fonts.large)


def create_image(replay):
    _name = 'talents.png'
    hots.print_log('ImageStartCreateTalentsImage', level=0)
    hots.print_log('ImageLoadBackGround', level=0)
    image = load_background()

    hots.print_log('ImageCreateIcons', level=0)
    create_icons(image)

    hots.print_log('ImageAddHeroes', level=0)
    add_heroes(image, replay)

    hots.print_log('ImageAddOtherInfo', level=0)
    add_other_info(image, replay)

    hots.print_log('ImageSaveImageMatch', level=0)
    image.save(hots.paths.upload / _name)

    hots.print_log('ImageUploadTalents', level=2)
    url = hots.visual.upload.upload_file(hots.paths.upload / _name, _name)
    if hots.config.duplicate_url_in_console:
        hots.print_log('SendUrl', url, level=3)
    return url
