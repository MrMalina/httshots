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
    tmp = hots.strings['ImageMap']
    draw.text((380, 50), tmp, (255,255,255), font=hots.config.vs_font)
    tmp = hots.strings['ImageSide']
    draw.text((675, 50), tmp, (255,255,255), font=hots.config.vs_font)
    tmp = hots.strings['ImageResult']
    draw.text((825, 50), tmp, (255,255,255), font=hots.config.vs_font)
    tmp = hots.strings['ImageDuration']
    draw.text((975, 50), tmp, (255,255,255), font=hots.config.vs_font)

    tmp = Image.open(hots.config.vs_stats_path+'kill.png').convert('RGBA')
    image.paste(tmp, (1125, 50), mask=tmp)

    tmp = Image.open(hots.config.vs_stats_path+'assist.png').convert('RGBA')
    image.paste(tmp, (1185, 50), mask=tmp)

    tmp = Image.open(hots.config.vs_stats_path+'death.png').convert('RGBA')
    image.paste(tmp, (1245, 50), mask=tmp)


def add_games(image, replays):
    score_path = hots.config.vs_score_path
    blue = Image.open(score_path+'gold.png')
    bplayer = Image.open(score_path+'playergold.png').convert('RGBA')
    red = Image.open(score_path+'grey.png')
    rplayer = Image.open(score_path+'playergrey.png').convert('RGBA')
    glow = Image.open(score_path+'portrait.png').convert('RGBA')

    add = 100
    rng = 60

    for x, replay in enumerate(reversed(replays)):
        for player in replay.info.players.values():
            if player.name in hots.config.accounts:
                me = player
                break

        player = me

        hero_name = hots.hero_names.get_eng_hero(player.hero)
        hero = Image.open(hots.config.vs_heroes_path+hero_name+'.png').convert('RGBA')

        draw = ImageDraw.Draw(image)

        team_id = player.team_id
        time = player.time

        if player.result == 1:
            image.paste(bplayer, (25, add+(x*rng)), mask=bplayer)
            image.paste(blue, (105, add+(x*rng)), mask=blue)
            image.paste(hero, (40, add+(x*rng)), mask=glow)
            draw.text((155, add+(x*rng)+30), player.name, (105,156,249), font=hots.config.vs_font)
            color = (105,156,249)
            postfix = 'blue'

        else:
            image.paste(rplayer, (25, add+(x*rng)), mask=rplayer)
            image.paste(red, (105, add+(x*rng)), mask=red)
            image.paste(hero, (40, add+(x*rng)), mask=glow)
            draw.text((155, add+(x*rng)+30), player.name, (234,140,140), font=hots.config.vs_font)
            color = (234,140,140)
            postfix = 'red'

        hero_short_name = hots.hero_names.get_short_hero(player.hero)
        draw.text((155, add+(x*rng)+10), hero_short_name, (255,255,255), font=hots.config.vs_font)

        for mvp in hots.visual.mvps:
            if getattr(player, 'award_'+mvp):
                tmp = Image.open(hots.config.vs_mvp_path+f'{hots.visual.mvps[mvp]}_{postfix}.png')
                tmp = tmp.resize((48, 48))
                image.paste(tmp, (320, add+(x*rng)+4), mask=tmp)

        draw.text((380, add+(x*rng)+20), replay.info.details.title, color, font=hots.config.vs_font)

        if team_id == 0:
            tmp = hots.strings['GameTeamBlue']
            draw.text((675, add+(x*rng)+20), tmp, color, font=hots.config.vs_font)
        else:
            tmp = hots.strings['GameTeamRed']
            draw.text((675, add+(x*rng)+20), tmp, color, font=hots.config.vs_font)

        if player.result == 1:
            tmp = hots.strings['GameResultWin']
            draw.text((825, add+(x*rng)+20), tmp, color, font=hots.config.vs_font)
        else:
            tmp = hots.strings['GameResultLose']
            draw.text((825, add+(x*rng)+20), tmp, color, font=hots.config.vs_font)

        draw.text((1000, add+(x*rng)+20), f"{str(time//60).zfill(2)}:{str(time%60).zfill(2)}", 
                  color, font=hots.config.vs_font)

        solo_kill = str(player.solo_kill)
        shift = get_shift(solo_kill)
        draw.text((1125-shift, add+(x*rng)+20), solo_kill, color, font=hots.config.vs_font)

        assists = str(player.assists)
        shift = get_shift(assists)
        draw.text((1185-shift, add+(x*rng)+20), assists, color, font=hots.config.vs_font)

        deaths = str(player.deaths)
        shift = get_shift(deaths)
        draw.text((1245-shift, add+(x*rng)+20), deaths, color, font=hots.config.vs_font)


def get_shift(value):
    ln = len(value)
    if ln == 6:
        return 11.5
    if ln == 5:
        return 8
    if ln == 4:
        return 5
    if ln == 3:
        return 4
    if ln == 2:
        return -5
    if ln == 1:
        return -11

    return 0


def add_other_info(image, replays):
    wins = 0
    loses = 0

    for replay in replays:
        for player in replay.info.players.values():
            if player.name in hots.config.accounts:
                if player.result == 1:
                    wins += 1
                else:
                    loses += 1

    draw = ImageDraw.Draw(image)
    tmp = hots.strings['Wins'][2]
    draw.text((125, 700), tmp, (185,213,255), font=hots.config.vs_large_font)
    draw.text((150, 725), f"{wins}", (39,153,165), font=hots.config.vs_big_font)

    tmp = hots.strings['Loses'][2]
    draw.text((1350-260, 700), tmp, (234,140,140), font=hots.config.vs_large_font)
    draw.text((1350-200, 725), f"{loses}", (175,76,105), font=hots.config.vs_big_font)

    tmp = hots.strings['ImageTotalGames']
    draw.text((1350/2-40, 700), tmp, (138,166,251), font=hots.config.vs_large_font)
    draw.text((1350/2, 725), f"{len(replays)}", (255, 255, 255), font=hots.config.vs_big_font)


def create_image(*args):
    _name = 'games.png'

    hots.print_log('ImageStartCreateGamesImage', uwaga=0)
    hots.print_log('ImageCreateBorder', uwaga=0)
    image = create_board()

    hots.print_log('ImageGetReplays', uwaga=0)
    replays = hots.stream_replays
    if len(replays) <= 10:
        replays = replays[:10]
    else:
        replays = replays[len(replays)-10:len(replays)]

    hots.print_log('ImageCreateIcons', uwaga=0)
    create_icons(image)

    hots.print_log('ImageAddGames', len(replays), uwaga=0)
    add_games(image, replays)

    hots.print_log('ImageAddOtherInfo', uwaga=0)
    add_other_info(image, replays)

    hots.print_log('ImageSaveImageGames', uwaga=0)
    image.save(hots.config.vs_screens_path + _name)

    hots.print_log('ImageUploadGames')
    url = hots.visual.upload.upload_file(hots.config.vs_screens_path + _name, _name)

    return url
