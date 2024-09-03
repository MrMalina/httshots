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
border_files = path + "border/"
stats_files = path + "stats/"
score_files = path + "scorescreen/"
heroes_files = path + "heroes/"
font_files = path + "ttf/"
screens_files = path + "screens/"
mvp_files = path + "mvp/"
font = ImageFont.truetype(font_files+'Exo2-Bold.ttf', 16)
large_font = ImageFont.truetype(font_files+'Exo2-Bold.ttf', 24)
big_font = ImageFont.truetype(font_files+'Exo2-Bold.ttf', 46)


# ======================================================================
# >> FUNCTIONS
# ======================================================================
def create_board():
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
    draw.text((360, 50), "Карта", (255,255,255), font=font)
    draw.text((675, 50), "Команда", (255,255,255), font=font)
    draw.text((825, 50), "Результат", (255,255,255), font=font)
    draw.text((975, 50), "Длительность", (255,255,255), font=font)

    tmp = Image.open(stats_files+'kill.png').convert('RGBA')
    image.paste(tmp, (1125, 50), mask=tmp)

    tmp = Image.open(stats_files+'assist.png').convert('RGBA')
    image.paste(tmp, (1185, 50), mask=tmp)

    tmp = Image.open(stats_files+'death.png').convert('RGBA')
    image.paste(tmp, (1245, 50), mask=tmp)


def add_games(image, replays):
    blue = Image.open(score_files+'gold.png')
    bplayer = Image.open(score_files+'playergold.png').convert('RGBA')
    red = Image.open(score_files+'grey.png')
    rplayer = Image.open(score_files+'playergrey.png').convert('RGBA')
    glow = Image.open(score_files+'portrait.png').convert('RGBA')

    add = 100
    rng = 60

    for x, replay in enumerate(replays):
        red_kills = 0
        blue_kills = 0

        for player in replay.info.players.values():
            if player.name in httshots.config['ACCOUNTS']:
                me = player
                break

        player = me

        hero_name = httshots.heroes['heroes_en'][player.hero].lower()
        hero = Image.open(heroes_files+hero_name+'.png').convert('RGBA')

        draw = ImageDraw.Draw(image)

        team_id = player.team_id
        id = player.userid
        time = player.time

        if player.result == 1:
            image.paste(bplayer, (25, add+(x*rng)), mask=bplayer)
            image.paste(blue, (105, add+(x*rng)), mask=blue)
            image.paste(hero, (40, add+(x*rng)), mask=glow)
            draw.text((155, add+(x*rng)+30), player.name, (105,156,249), font=font)
            color = (105,156,249)
            postfix = 'blue'

        else:
            image.paste(rplayer, (25, add+(x*rng)), mask=rplayer)
            image.paste(red, (105, add+(x*rng)), mask=red)
            image.paste(hero, (40, add+(x*rng)), mask=glow)
            draw.text((155, add+(x*rng)+30), player.name, (234,140,140), font=font)
            color = (234,140,140)
            postfix = 'red'

        draw.text((155, add+(x*rng)+10), httshots.heroes['heroes_short'].get(player.hero, player.hero), (255,255,255), font=font)

        for mvp in httshots.score.mvps:
            if getattr(player, 'award_'+mvp):
                tmp = Image.open(mvp_files+f'{httshots.score.mvps[mvp]}_{postfix}.png')
                tmp = tmp.resize((48, 48))
                image.paste(tmp, (270, add+(x*rng)+4), mask=tmp)

        draw.text((360, add+(x*rng)+20), replay.info.details.title, color, font=font)

        if team_id == 0:
            draw.text((675, add+(x*rng)+20), "Синяя", color, font=font)
        else:
            draw.text((675, add+(x*rng)+20), "Красная", color, font=font)

        if player.result == 1:
            draw.text((825, add+(x*rng)+20), "Победа", color, font=font)
        else:
            draw.text((825, add+(x*rng)+20), "Поражение", color, font=font)

        draw.text((1000, add+(x*rng)+20), f"{time//60}:{time%60}", color, font=font)

        solo_kill = str(player.solo_kill)
        shift = get_shift(solo_kill)
        draw.text((1125-shift, add+(x*rng)+20), solo_kill, color, font=font)

        assists = str(player.assists)
        shift = get_shift(assists)
        draw.text((1185-shift, add+(x*rng)+20), assists, color, font=font)

        deaths = str(player.deaths)
        shift = get_shift(deaths)
        draw.text((1245-shift, add+(x*rng)+20), deaths, color, font=font)


def get_shift(value):
    ln = len(value)
    if ln == 6:
        return 11.5
    elif ln == 5:
        return 8
    elif ln == 4:
        return 5
    elif ln == 3:
        return 4
    elif ln == 2:
        return -5
    elif ln == 1:
        return -11

    return 0


def add_other_info(image, replays):
    wins = 0
    loses = 0

    for replay in replays:
        for player in replay.info.players.values():
            if player.name in httshots.config['ACCOUNTS']:
                if player.result == 1:
                    wins += 1
                else:
                    loses += 1
                

    draw = ImageDraw.Draw(image)
    draw.text((125, 700), 'Побед', (185,213,255), font=large_font)
    draw.text((150, 730), f"{wins}", (39,153,165), font=big_font)

    draw.text((1350-260, 700), 'Поражений', (234,140,140), font=large_font)
    draw.text((1350-200, 730), f"{loses}", (175,76,105), font=big_font)

    draw.text((1350/2-40, 700), 'Всего игр', (138,166,251), font=large_font)
    draw.text((1350/2, 730), f"{len(replays)}", (255, 255, 255), font=big_font)


def upload_image():
    try:
        url = httshots.imgur.upload_from_path(screens_files + 'vavaviva_games.png')
        if 'link' in url:
            return url['link'].replace('i.imgur', 'imgur')
        return None
    except Exception as e:
        print(e)
        return None


def create_image():
    httshots.print_log('ImgurStartCreateImage', 1)
    httshots.print_log('ImgurCreateBorder', 1)
    image = create_board()

    httshots.print_log('ImgurGetReplays', 1)
    replays = httshots.stream_replays
    if len(replays) <= 10:
        replays = replays[:10]
    else:
        replays = replays[len(replays)-10:len(replays)]

    httshots.print_log('ImgurCreateIcons', 1)
    create_icons(image)

    httshots.print_log('ImgurAddGames', 1, len(replays))
    add_games(image, replays)

    httshots.print_log('ImgurAddOtherInfo', 1)
    add_other_info(image, replays)

    httshots.print_log('ImgurSaveImageGames', 1)
    image.save(screens_files + 'vavaviva_games.png')

    httshots.print_log('ImgurUploadImageGames', 1)
    url = upload_image()
    return url
