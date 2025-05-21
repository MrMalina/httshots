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
    return Image.open(hots.paths.bg / 'match_background.png')


def create_icons(image):
    tmp = Image.open(hots.paths.stats / 'kill.png').convert('RGBA')
    image.paste(tmp, (340, 50), mask=tmp)

    tmp = Image.open(hots.paths.stats / 'assist.png').convert('RGBA')
    image.paste(tmp, (400, 50), mask=tmp)

    tmp = Image.open(hots.paths.stats / 'death.png').convert('RGBA')
    image.paste(tmp, (460, 50), mask=tmp)

    tmp = Image.open(hots.paths.stats / 'siegedamage.png').convert('RGBA')
    image.paste(tmp, (560, 50), mask=tmp)

    tmp = Image.open(hots.paths.stats / 'miniondamage.png').convert('RGBA')
    image.paste(tmp, (660, 50), mask=tmp)

    tmp = Image.open(hots.paths.stats / 'herodamage.png').convert('RGBA')
    image.paste(tmp, (760, 50), mask=tmp)

    tmp = Image.open(hots.paths.stats / 'takendamage.png').convert('RGBA')
    image.paste(tmp, (860, 50), mask=tmp)

    tmp = Image.open(hots.paths.stats / 'heal.png').convert('RGBA')
    image.paste(tmp, (960, 50), mask=tmp)

    tmp = Image.open(hots.paths.stats / 'selfheal.png').convert('RGBA')
    image.paste(tmp, (1060, 50), mask=tmp)

    tmp = Image.open(hots.paths.stats / 'bossdamage.png').convert('RGBA')
    image.paste(tmp, (1160, 50), mask=tmp)

    tmp = Image.open(hots.paths.stats / 'xp.png').convert('RGBA')
    image.paste(tmp, (1260, 50), mask=tmp)


def get_max_stats(replay):
    max_stats = {0: {}, 1: {}}
    stats = ['solo_kill', 'assists', 'deaths', 'structure_damage', 'minion_damage',
             'hero_damage', 'taken_damage', 'healing', 'self_healing', 'merc_camps',
             'experience']

    for stat in stats:
        max_stats[0][stat] = 0
        max_stats[1][stat] = 0

        for player in replay.players.values():
            value = getattr(player, stat)
            team_id = player.team_id
            id = player.userid
            if not max_stats[team_id][stat]:
                max_stats[team_id][stat] = [[id], value]
                continue

            if value > max_stats[team_id][stat][1]:
                max_stats[team_id][stat] = [[id], value]

            elif value == max_stats[team_id][stat][1]:
                max_stats[team_id][stat][0].append(id)

    return max_stats


def add_heroes(image, replay, max_stats):
    blue = Image.open(hots.paths.score / 'blue.png')
    bplayer = Image.open(hots.paths.score / 'playerblue.png').convert('RGBA')
    red = Image.open(hots.paths.score / 'red.png')
    rplayer = Image.open(hots.paths.score / 'playerred.png').convert('RGBA')
    glow = Image.open(hots.paths.score / 'portrait.png').convert('RGBA')

    add = 100
    rng = 60

    for x, player in enumerate(replay.players.values()):
        hero_name = hots.htts_data.get_eng_hero(player.hero)
        hero = Image.open(hots.paths.heroes / (hero_name.lower() + '.png')).convert('RGBA')

        draw = ImageDraw.Draw(image)

        team_id = player.team_id
        id = player.userid

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
            color = (105,156,249)
            postfix = 'blue'

        else:
            image.paste(rplayer, (25, add+(x*rng)), mask=rplayer)
            image.paste(red, (25+rplayer.size[0], add+(x*rng)), mask=red)
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
                image.paste(tmp, (270, add+(x*rng)+4), mask=tmp)

        solo_kill = str(player.solo_kill)
        shift = get_shift(solo_kill)
        draw.text((340-shift, add+(x*rng)+20), solo_kill, color, font=hots.fonts.default)

        assists = str(player.assists)
        shift = get_shift(assists)
        draw.text((400-shift, add+(x*rng)+20), assists, color, font=hots.fonts.default)

        deaths = str(player.deaths)
        shift = get_shift(deaths)
        draw.text((460-shift, add+(x*rng)+20), deaths, color, font=hots.fonts.default)

        structure_dmg = str(player.structure_damage)
        shift = get_shift(structure_dmg)
        if id in max_stats[team_id]['structure_damage'][0]:
            draw.text((560-shift, add+(x*rng)+20), structure_dmg, WHITE, font=hots.fonts.default)
        else:
            draw.text((560-shift, add+(x*rng)+20), structure_dmg, color, font=hots.fonts.default)

        minion_dmg = str(player.minion_damage)
        shift = get_shift(minion_dmg)
        if id in max_stats[team_id]['minion_damage'][0]:
            draw.text((660-shift, add+(x*rng)+20), minion_dmg, WHITE, font=hots.fonts.default)
        else:
            draw.text((660-shift, add+(x*rng)+20), minion_dmg, color, font=hots.fonts.default)

        hero_dmg = str(player.hero_damage)
        shift = get_shift(hero_dmg)
        if id in max_stats[team_id]['hero_damage'][0]:
            draw.text((760-shift, add+(x*rng)+20), hero_dmg, WHITE, font=hots.fonts.default)
        else:
            draw.text((760-shift, add+(x*rng)+20), hero_dmg, color, font=hots.fonts.default)

        taken_dmg = str(player.taken_damage)
        shift = get_shift(taken_dmg)
        if id in max_stats[team_id]['taken_damage'][0]:
            draw.text((860-shift, add+(x*rng)+20), taken_dmg, WHITE, font=hots.fonts.default)
        else:
            draw.text((860-shift, add+(x*rng)+20), taken_dmg, color, font=hots.fonts.default)

        healing = str(player.healing)
        shift = get_shift(healing)
        if healing == '0': healing = '-'
        if id in max_stats[team_id]['healing'][0]:
            draw.text((960-shift, add+(x*rng)+20), healing, WHITE, font=hots.fonts.default)
        else:
            draw.text((960-shift, add+(x*rng)+20), healing, color, font=hots.fonts.default)

        self_healing = str(player.self_healing)
        shift = get_shift(self_healing)
        if self_healing == '0': self_healing = '-'
        if id in max_stats[team_id]['self_healing'][0]:
            draw.text((1060-shift, add+(x*rng)+20), self_healing, WHITE, font=hots.fonts.default)
        else:
            draw.text((1060-shift, add+(x*rng)+20), self_healing, color, font=hots.fonts.default)

        merc_camps = str(player.merc_camps)
        shift = get_shift(merc_camps)
        if merc_camps == '0': merc_camps = '-'
        if id in max_stats[team_id]['merc_camps'][0]:
            draw.text((1160-shift, add+(x*rng)+20), merc_camps, WHITE, font=hots.fonts.default)
        else:
            draw.text((1160-shift, add+(x*rng)+20), merc_camps, color, font=hots.fonts.default)

        experience = str(player.experience)
        shift = get_shift(experience)
        if id in max_stats[team_id]['experience'][0]:
            draw.text((1260-shift, add+(x*rng)+20), experience, WHITE, font=hots.fonts.default)
        else:
            draw.text((1260-shift, add+(x*rng)+20), experience, color, font=hots.fonts.default)


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


def add_other_info(image, replay):
    redkills = Image.open(hots.paths.stats / 'redkills.png')
    bluekills = Image.open(hots.paths.stats / 'bluekills.png')
    language = hots.config.language

    red_kills = 0
    blue_kills = 0
    for player in replay.players.values():
        if player.team_id == 0:
            blue_level = player.team_level
            blue_kills += player.solo_kill
        else:
            red_level = player.team_level
            red_kills += player.solo_kill

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
    draw.text((290, 715), str(blue_kills), (185,213,255), font=hots.fonts.big)
    image.paste(bluekills, (360, 725), mask=bluekills)

    tmp = hots.strings('ImageLevelTeam', red_level)
    draw.text((1350-250, 710), hots.strings['ImageRedTeam'], (234,140,140), font=hots.fonts.large)
    draw.text((1350-250, 740), tmp, (175,76,105), font=hots.fonts.large)
    draw.text((1350-330, 715), str(red_kills), (185,213,255), font=hots.fonts.big)
    image.paste(redkills, (1350-390, 725), mask=redkills)

    if language == 'ru':
        coords = (550, 720)
    else:
        coords = (580, 720)

    tmp = hots.strings['ImageMatchDuration']
    draw.text(coords, tmp, (138,166,251), font=hots.fonts.large)
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
    _name = 'match.png'
    hots.print_log('ImageStartCreateMatchImage', uwaga=0)
    hots.print_log('ImageLoadBackGround', uwaga=0)
    image = load_background()

    hots.print_log('ImageCreateIcons', uwaga=0)
    create_icons(image)

    hots.print_log('ImageGetMaxStats', uwaga=0)
    max_stats = get_max_stats(replay)

    hots.print_log('ImageAddHeroes', uwaga=0)
    add_heroes(image, replay, max_stats)

    hots.print_log('ImageAddOtherInfo', uwaga=0)
    add_other_info(image, replay)

    hots.print_log('ImageSaveImageMatch', uwaga=0)
    image.save(hots.paths.upload / _name)

    hots.print_log('ImageUploadMatch')
    url = hots.visual.upload.upload_file(hots.paths.upload / _name, _name)
    if hots.config.send_url_to_console:
        hots.print_log('SendUrl', url)
    return url
