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
GREEN = (105,249,105)
RTEAM = (234,140,140)


# ======================================================================
# >> FUNCTIONS
# ======================================================================
def load_background():
    return Image.open(hots.paths.bg / 'games_background.png')


def create_icons(image):
    draw = ImageDraw.Draw(image)
    tmp = hots.strings['ImageMap']
    draw.text((380, 50), tmp, WHITE, font=hots.fonts.default)
    tmp = hots.strings['ImageSide']
    draw.text((675, 50), tmp, WHITE, font=hots.fonts.default)
    tmp = hots.strings['ImageResult']
    draw.text((825, 50), tmp, WHITE, font=hots.fonts.default)
    tmp = hots.strings['ImageDuration']
    draw.text((975, 50), tmp, WHITE, font=hots.fonts.default)

    tmp = Image.open(hots.paths.stats / 'kill.png').convert('RGBA')
    image.paste(tmp, (1125, 50), mask=tmp)

    tmp = Image.open(hots.paths.stats / 'assist.png').convert('RGBA')
    image.paste(tmp, (1185, 50), mask=tmp)

    tmp = Image.open(hots.paths.stats / 'death.png').convert('RGBA')
    image.paste(tmp, (1245, 50), mask=tmp)


def add_games(image, replays):
    blue = Image.open(hots.paths.score / 'gold.png')
    bplayer = Image.open(hots.paths.score / 'playergold.png').convert('RGBA')
    red = Image.open(hots.paths.score / 'grey.png')
    rplayer = Image.open(hots.paths.score / 'playergrey.png').convert('RGBA')
    glow = Image.open(hots.paths.score / 'portrait.png').convert('RGBA')

    add = 100
    rng = 60

    for x, replay in enumerate(reversed(replays)):
        for player in replay.info.players.values():
            if player.name in hots.config.accounts:
                me = player
                break

        player = me

        hero_name = hots.htts_data.get_eng_hero(player.hero)
        hero = Image.open(hots.paths.heroes / (hero_name + '.png')).convert('RGBA')

        draw = ImageDraw.Draw(image)

        team_id = player.team_id
        time = player.time

        name = player.name
        check = hots.visual.check_name.match(name)[0]
        if check:
            name_font = hots.fonts.default
        else:
            name_font = hots.fonts.ch_default

        if player.result == 1:
            image.paste(bplayer, (25, add+(x*rng)), mask=bplayer)
            image.paste(blue, (105, add+(x*rng)), mask=blue)
            image.paste(hero, (40, add+(x*rng)), mask=glow)
            draw.text((155, add+(x*rng)+30), name, BTEAM, font=name_font)
            color = (105,156,249)
            postfix = 'blue'

        else:
            image.paste(rplayer, (25, add+(x*rng)), mask=rplayer)
            image.paste(red, (105, add+(x*rng)), mask=red)
            image.paste(hero, (40, add+(x*rng)), mask=glow)
            draw.text((155, add+(x*rng)+30), name, RTEAM, font=name_font)
            color = (234,140,140)
            postfix = 'red'

        hero_short_name = hots.htts_data.get_short_hero(player.hero)
        draw.text((155, add+(x*rng)+10), hero_short_name, WHITE, font=hots.fonts.default)

        for mvp in hots.visual.mvps:
            if getattr(player, 'award_'+mvp):
                tmp = Image.open(hots.paths.mvp / f'{hots.visual.mvps[mvp]}_{postfix}.png')
                tmp = tmp.resize((48, 48))
                image.paste(tmp, (320, add+(x*rng)+4), mask=tmp)

        draw.text((380, add+(x*rng)+20), replay.info.details.title, WHITE, font=hots.fonts.default)

        if team_id == 0:
            tmp = hots.strings['GameTeamBlue']
            draw.text((675, add+(x*rng)+20), tmp, BTEAM, font=hots.fonts.default)
        else:
            tmp = hots.strings['GameTeamRed']
            draw.text((675, add+(x*rng)+20), tmp, RTEAM, font=hots.fonts.default)

        if player.result == 1:
            tmp = hots.strings['GameResultWin']
            draw.text((825, add+(x*rng)+20), tmp, GREEN, font=hots.fonts.default)
        else:
            tmp = hots.strings['GameResultLose']
            draw.text((825, add+(x*rng)+20), tmp, RTEAM, font=hots.fonts.default)

        draw.text((1000, add+(x*rng)+20), f"{str(time//60).zfill(2)}:{str(time%60).zfill(2)}",
                  WHITE, font=hots.fonts.default)

        solo_kill = str(player.solo_kill)
        shift = get_shift(solo_kill)
        draw.text((1125-shift, add+(x*rng)+20), solo_kill, color, font=hots.fonts.default)

        assists = str(player.assists)
        shift = get_shift(assists)
        draw.text((1185-shift, add+(x*rng)+20), assists, color, font=hots.fonts.default)

        deaths = str(player.deaths)
        shift = get_shift(deaths)
        draw.text((1245-shift, add+(x*rng)+20), deaths, color, font=hots.fonts.default)


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
    draw.text((125, 700), tmp, (185,213,255), font=hots.fonts.large)
    draw.text((150, 725), f"{wins}", (39,153,165), font=hots.fonts.big)

    tmp = hots.strings['Loses'][2]
    draw.text((1350-260, 700), tmp, (234,140,140), font=hots.fonts.large)
    draw.text((1350-200, 725), f"{loses}", (175,76,105), font=hots.fonts.big)

    tmp = hots.strings['ImageTotalGames']
    draw.text((1350/2-40, 700), tmp, (138,166,251), font=hots.fonts.large)
    draw.text((1350/2, 725), f"{len(replays)}", WHITE, font=hots.fonts.big)


def create_image():
    _name = 'games.png'

    hots.print_log('ImageStartCreateGamesImage', uwaga=0)
    hots.print_log('ImageLoadBackGround', uwaga=0)
    image = load_background()

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
    image.save(hots.paths.upload / _name)

    hots.print_log('ImageUploadGames')
    url = hots.visual.upload.upload_file(hots.paths.upload / _name, _name)
    if hots.config.send_url_to_console:
        hots.print_log('SendUrl', url)
    return url
