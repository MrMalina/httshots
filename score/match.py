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
    tmp = Image.open(stats_files+'kill.png').convert('RGBA')
    image.paste(tmp, (340, 50), mask=tmp)

    tmp = Image.open(stats_files+'assist.png').convert('RGBA')
    image.paste(tmp, (400, 50), mask=tmp)

    tmp = Image.open(stats_files+'death.png').convert('RGBA')
    image.paste(tmp, (460, 50), mask=tmp)

    tmp = Image.open(stats_files+'siegedamage.png').convert('RGBA')
    image.paste(tmp, (560, 50), mask=tmp)

    tmp = Image.open(stats_files+'miniondamage.png').convert('RGBA')
    image.paste(tmp, (660, 50), mask=tmp)

    tmp = Image.open(stats_files+'herodamage.png').convert('RGBA')
    image.paste(tmp, (760, 50), mask=tmp)

    tmp = Image.open(stats_files+'takendamage.png').convert('RGBA')
    image.paste(tmp, (860, 50), mask=tmp)

    tmp = Image.open(stats_files+'heal.png').convert('RGBA')
    image.paste(tmp, (960, 50), mask=tmp)

    tmp = Image.open(stats_files+'selfheal.png').convert('RGBA')
    image.paste(tmp, (1060, 50), mask=tmp)

    tmp = Image.open(stats_files+'bossdamage.png').convert('RGBA')
    image.paste(tmp, (1160, 50), mask=tmp)

    tmp = Image.open(stats_files+'xp.png').convert('RGBA')
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
    blue = Image.open(score_files+'blue.png')
    bplayer = Image.open(score_files+'playerblue.png').convert('RGBA')
    red = Image.open(score_files+'red.png')
    rplayer = Image.open(score_files+'playerred.png').convert('RGBA')
    glow = Image.open(score_files+'portrait.png').convert('RGBA')
    language = httshots.language

    add = 100
    rng = 60

    for x, player in enumerate(replay.players.values()):
        hero_name = httshots.heroes['heroes_en'][player.hero]
        hero = Image.open(heroes_files+hero_name.lower()+'.png').convert('RGBA')

        draw = ImageDraw.Draw(image)

        team_id = player.team_id
        id = player.userid

        if team_id == 0:
            image.paste(bplayer, (25, add+(x*rng)), mask=bplayer)
            image.paste(blue, (25+rplayer.size[0], add+(x*rng)), mask=blue)
            image.paste(hero, (40, add+(x*rng)), mask=glow)
            draw.text((155, add+(x*rng)+30), player.name, (105,156,249), font=font)
            color = (105,156,249)
            postfix = 'blue'

        else:
            image.paste(rplayer, (25, add+(x*rng)), mask=rplayer)
            image.paste(red, (25+rplayer.size[0], add+(x*rng)), mask=red)
            image.paste(hero, (40, add+(x*rng)), mask=glow)
            draw.text((155, add+(x*rng)+30), player.name, (234,140,140), font=font)
            color = (234,140,140)
            postfix = 'red'

        if 'heroes_'+language in httshots.heroes:
            hero_short_name = httshots.heroes['heroes_'+language].get(hero_name, hero_name)
        elif language == 'ru':
            hero_short_name = httshots.heroes['heroes_short'].get(player.hero, player.hero)
        else:
            hero_short_name = hero_name

        draw.text((155, add+(x*rng)+10), hero_short_name, (255,255,255), font=font)

        for mvp in httshots.score.mvps:
            if getattr(player, 'award_'+mvp):
                tmp = Image.open(mvp_files+f'{httshots.score.mvps[mvp]}_{postfix}.png')
                tmp = tmp.resize((48, 48))
                image.paste(tmp, (270, add+(x*rng)+4), mask=tmp)

        solo_kill = str(player.solo_kill)
        shift = get_shift(solo_kill)
        draw.text((340-shift, add+(x*rng)+20), solo_kill, color, font=font)

        assists = str(player.assists)
        shift = get_shift(assists)
        draw.text((400-shift, add+(x*rng)+20), assists, color, font=font)

        deaths = str(player.deaths)
        shift = get_shift(deaths)
        draw.text((460-shift, add+(x*rng)+20), deaths, color, font=font)

        structure_damage = str(player.structure_damage)
        shift = get_shift(structure_damage)
        if id in max_stats[team_id]['structure_damage'][0]:
            draw.text((560-shift, add+(x*rng)+20), structure_damage, (255, 255, 255), font=font)
        else:
            draw.text((560-shift, add+(x*rng)+20), structure_damage, color, font=font)

        minion_damage = str(player.minion_damage)
        shift = get_shift(minion_damage)
        if id in max_stats[team_id]['minion_damage'][0]:
            draw.text((660-shift, add+(x*rng)+20), minion_damage, (255, 255, 255), font=font)
        else:
            draw.text((660-shift, add+(x*rng)+20), minion_damage, color, font=font)

        hero_damage = str(player.hero_damage)
        shift = get_shift(hero_damage)
        if id in max_stats[team_id]['hero_damage'][0]:
            draw.text((760-shift, add+(x*rng)+20), hero_damage, (255, 255, 255), font=font)
        else:
            draw.text((760-shift, add+(x*rng)+20), hero_damage, color, font=font)

        taken_damage = str(player.taken_damage)
        shift = get_shift(taken_damage)
        if id in max_stats[team_id]['taken_damage'][0]:
            draw.text((860-shift, add+(x*rng)+20), taken_damage, (255, 255, 255), font=font)
        else:
            draw.text((860-shift, add+(x*rng)+20), taken_damage, color, font=font)

        healing = str(player.healing)
        shift = get_shift(healing)
        if healing == '0': healing = '-'
        if id in max_stats[team_id]['healing'][0]:
            draw.text((960-shift, add+(x*rng)+20), healing, (255, 255, 255), font=font)
        else:
            draw.text((960-shift, add+(x*rng)+20), healing, color, font=font)

        self_healing = str(player.self_healing)
        shift = get_shift(self_healing)
        if self_healing == '0': self_healing = '-'
        if id in max_stats[team_id]['self_healing'][0]:
            draw.text((1060-shift, add+(x*rng)+20), self_healing, (255, 255, 255), font=font)
        else:
            draw.text((1060-shift, add+(x*rng)+20), self_healing, color, font=font)

        merc_camps = str(player.merc_camps)
        shift = get_shift(merc_camps)
        if merc_camps == '0': merc_camps = '-'
        if id in max_stats[team_id]['merc_camps'][0]:
            draw.text((1160-shift, add+(x*rng)+20), merc_camps, (255, 255, 255), font=font)
        else:
            draw.text((1160-shift, add+(x*rng)+20), merc_camps, color, font=font)

        experience = str(player.experience)
        shift = get_shift(experience)
        if id in max_stats[team_id]['experience'][0]:
            draw.text((1260-shift, add+(x*rng)+20), experience, (255, 255, 255), font=font)
        else:
            draw.text((1260-shift, add+(x*rng)+20), experience, color, font=font)


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


def add_other_info(image, replay):
    redkills = Image.open(stats_files+'redkills.png')
    bluekills = Image.open(stats_files+'bluekills.png')
    language = httshots.language

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
    if language == 'RU':
        coords = (80, 710)
    else:
        coords = (105, 710)

    draw.text(coords, httshots.strings['ImageBlueTeam'], (185,213,255), font=large_font)
    draw.text((105, 740), httshots.strings('ImageLevelTeam', blue_level), (39,153,165), font=large_font)
    draw.text((290, 715), str(blue_kills), (185,213,255), font=big_font)
    image.paste(bluekills, (360, 725), mask=bluekills)

    draw.text((1350-250, 710), httshots.strings['ImageRedTeam'], (234,140,140), font=large_font)
    draw.text((1350-250, 740), httshots.strings('ImageLevelTeam', red_level), (175,76,105), font=large_font)
    draw.text((1350-330, 715), str(red_kills), (185,213,255), font=big_font)
    image.paste(redkills, (1350-390, 725), mask=redkills)

    if language == 'RU':
        coords = (555, 720)
    else:
        coords = (580, 720)

    draw.text(coords, httshots.strings['ImageMatchDuration'], (138,166,251), font=large_font)
    draw.text((610, 750), f"{time//60}:{time%60}", (255, 255, 255), font=big_font)

    if player.result == 1:
        if player.team_id == 0:
            text = httshots.strings['ImageBlueWin']
            color = (39,153,165)
        else:
            text = httshots.strings['ImageRedWin']
            color = (175,76,105)
    else:
        if player.team_id == 0:
            text = httshots.strings['ImageRedWin']
            color = (175,76,105)
        else:
            text = httshots.strings['ImageBlueWin']
            color = (39,153,165)

    draw.text((40, 50), text, color, font=large_font)


def upload_image():
    try:
        url = httshots.imgur.upload_from_path(screens_files + 'vavaviva.png')
        if 'link' in url:
            return url['link'].replace('i.', '')
        return None
    except Exception as e:
        print(e)
        return None


def create_image(replay):
    httshots.print_log('ImgurStartCreateImage', 1)
    httshots.print_log('ImgurCreateBorder', 1)
    image = create_board()

    httshots.print_log('ImgurCreateIcons', 1)
    create_icons(image)

    httshots.print_log('ImgurGetMaxStats', 1)
    max_stats = get_max_stats(replay)

    httshots.print_log('ImgurAddHeroes', 1)
    add_heroes(image, replay, max_stats)

    httshots.print_log('ImgurAddOtherInfo', 1)
    add_other_info(image, replay)

    httshots.print_log('ImgurSaveImageMatch', 1)
    image.save(screens_files + 'vavaviva.png')

    httshots.print_log('ImgurUploadImageMatch', 1)
    url = upload_image()
    return url
