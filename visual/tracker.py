# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
from PIL import Image
from PIL import ImageDraw

# Httshots
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


def add_heroes(image, players):
    blue = Image.open(hots.paths.utils / 'blue.png')
    bplayer = Image.open(hots.paths.utils / 'playerblue.png').convert('RGBA')
    red = Image.open(hots.paths.utils / 'red.png')
    rplayer = Image.open(hots.paths.utils / 'playerred.png').convert('RGBA')
    glow = Image.open(hots.paths.utils / 'portrait.png').convert('RGBA')

    t_available = Image.open(hots.paths.talents / 'talent_available.png')
    t_available_ult = Image.open(hots.paths.talents / 'talent_available_ult.png')
    t_bg = Image.open(hots.paths.talents / 'talent_bg.png')

    add = 100
    rng = 60

    _gameloop = 0
    for x, player in enumerate(players):
        hero_name = hots.htts_data.get_hero(player.hero)
        img_name = hots.htts_data.get_img_hero(hero_name)
        img_name = 'portrait_' + img_name + '.png'
        hero = Image.open(hots.paths.heroes / img_name).convert('RGBA')

        draw = ImageDraw.Draw(image)
        team_id = player.userid > 4

        btag = player.battle_tag
        name = hots.visual.check_name.match(btag)[0]
        if name:
            name_font = hots.fonts.default
        else:
            name_font = hots.fonts.ch_default

        if team_id == 0:
            image.paste(bplayer, (25, add+(x*rng)), mask=bplayer)
            image.paste(blue, (25+rplayer.size[0], add+(x*rng)), mask=blue)
            image.paste(hero, (40, add+(x*rng)), mask=glow)
            draw.text((155, add+(x*rng)+30), btag, BTEAM, font=name_font)

        else:
            image.paste(rplayer, (25, add+(x*rng)), mask=rplayer)
            image.paste(red, (25+rplayer.size[0], add+(x*rng)), mask=red)
            image.paste(hero, (40, add+(x*rng)), mask=glow)
            draw.text((155, add+(x*rng)+30), btag, RTEAM, font=name_font)

        tr_hero_name = hots.htts_data.get_translate_hero(player.hero, 0)
        hero_short_name = hots.htts_data.get_short_hero(tr_hero_name)
        draw.text((155, add+(x*rng)+10), hero_short_name, WHITE, font=hots.fonts.default)

        data_hero_name = hots.htts_data.get_data_name(hero_name)
        info = hots.hero_data[data_hero_name]['talents']
        talents = player.talents
        start = 500 - 30
        for z in zip([1, 4, 7, 10, 13, 16, 20], talents):
            level = z[0]
            talent = z[1]
            if talent == 0:
                image.paste(t_bg, (start+11, add+(x*rng+6)), mask=t_bg)
                start += 100
                continue

            icon = info['level'+str(level)][talent-1]['icon']
            icon = Image.open(hots.paths.talents /icon)
            icon = icon.resize((46, 46))
            image.paste(icon, (start+11, add+(x*rng+6)))

            if data_hero_name != 'Varian':
                if level != 10:
                    image.paste(t_available, (start, add+(x*rng-6)), mask=t_available)
                else:
                    image.paste(t_available_ult, (start, add+(x*rng-6)), mask=t_available_ult)
            else:
                if level != 4:
                    image.paste(t_available, (start, add+(x*rng-6)), mask=t_available)
                else:
                    image.paste(t_available_ult, (start, add+(x*rng-6)), mask=t_available_ult)

            start += 100

        if player._gameloop > _gameloop:
            _gameloop = player._gameloop

    _time = int((_gameloop - 610) / 16)
    if _time < 0:
        _time = 0

    _time = f"{str(_time//60).zfill(2)}:{str(_time%60).zfill(2)}"

    draw.text((580, 720), hots.strings['ImageTrackerTime'], (138,166,251), font=hots.fonts.large)
    draw.text((610, 745), _time, WHITE, font=hots.fonts.big)

    return _time


def create_image(players):
    _name = 'gametalents.png'
    hots.print_log('ImageStartCreateTalentsImage', level=0)
    hots.print_log('ImageLoadBackGround', level=0)
    image = load_background()

    hots.print_log('ImageCreateIcons', level=0)
    create_icons(image)

    hots.print_log('ImageAddHeroes', level=0)
    tmp = add_heroes(image, players)

    hots.print_log('ImageSaveImageMatch', level=0)
    image.save(hots.paths.upload / _name)

    hots.print_log('ImageUploadTracker', tmp, level=2)
    url = hots.visual.upload.upload_file(hots.paths.upload / _name,
                                 _name, True, 'curgame')
    return url


def send_talents(players):
    _name = 'info.log'
    with open(hots.paths.upload / _name, 'w', encoding="utf-8") as f:
        for _, player in enumerate(players):
            hero_name = hots.htts_data.get_hero(player.hero)
            hots_hero_name = hots.htts_data.remove_symbols(hero_name)
            tr_hero = hots.htts_data.get_translate_hero(hero_name, 0)
            talents = ''.join(map(str, player.talents))
            tmp = f" [T{talents},{hots_hero_name}]"
            icy_hero = hots.htts_data.get_icy_hero(hero_name).lower()
            icy_url = hots.ICY_URL.format(icy_hero, talents.replace('0', '-'))
            prep = f'<span>{tmp.strip()}</span>'
            tmp = ''.ljust(25-len(tmp))
            f.write(f'{tr_hero.ljust(20)} {prep} {tmp} - <a href="{icy_url}">Goto IcyVeins</a>\n')

    hots.visual.upload.upload_file(hots.paths.upload / _name,
                                   _name, True, 'curgame')
