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
def load_background():
    return Image.open(hots.config.vs_bg_path+'match_background.png')


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
    tmp = Image.open(hots.config.vs_stats_path+'kill.png').convert('RGBA')
    image.paste(tmp, (340, 50), mask=tmp)

    tmp = Image.open(hots.config.vs_stats_path+'assist.png').convert('RGBA')
    image.paste(tmp, (400, 50), mask=tmp)

    tmp = Image.open(hots.config.vs_stats_path+'death.png').convert('RGBA')
    image.paste(tmp, (460, 50), mask=tmp)

    tmp = Image.open(hots.config.vs_stats_path+'siegedamage.png').convert('RGBA')
    image.paste(tmp, (560, 50), mask=tmp)

    tmp = Image.open(hots.config.vs_stats_path+'miniondamage.png').convert('RGBA')
    image.paste(tmp, (660, 50), mask=tmp)

    tmp = Image.open(hots.config.vs_stats_path+'herodamage.png').convert('RGBA')
    image.paste(tmp, (760, 50), mask=tmp)

    tmp = Image.open(hots.config.vs_stats_path+'takendamage.png').convert('RGBA')
    image.paste(tmp, (860, 50), mask=tmp)

    tmp = Image.open(hots.config.vs_stats_path+'heal.png').convert('RGBA')
    image.paste(tmp, (960, 50), mask=tmp)

    tmp = Image.open(hots.config.vs_stats_path+'selfheal.png').convert('RGBA')
    image.paste(tmp, (1060, 50), mask=tmp)

    tmp = Image.open(hots.config.vs_stats_path+'bossdamage.png').convert('RGBA')
    image.paste(tmp, (1160, 50), mask=tmp)

    tmp = Image.open(hots.config.vs_stats_path+'xp.png').convert('RGBA')
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
    score_path = hots.config.vs_score_path
    blue = Image.open(score_path+'blue.png')
    bplayer = Image.open(score_path+'playerblue.png').convert('RGBA')
    red = Image.open(score_path+'red.png')
    rplayer = Image.open(score_path+'playerred.png').convert('RGBA')
    glow = Image.open(score_path+'portrait.png').convert('RGBA')

    add = 100
    rng = 60

    for x, player in enumerate(replay.players.values()):
        hero_name = hots.htts_data.get_eng_hero(player.hero)
        hero = Image.open(hots.config.vs_heroes_path+hero_name.lower()+'.png').convert('RGBA')

        draw = ImageDraw.Draw(image)

        team_id = player.team_id
        id = player.userid

        name = player.name
        check = hots.visual.check_name.match(name)[0]
        if check:
            name_font = hots.config.vs_font
        else:
            name_font = hots.config.vs_chinese_font

        if team_id == 0:
            image.paste(bplayer, (25, add+(x*rng)), mask=bplayer)
            image.paste(blue, (25+rplayer.size[0], add+(x*rng)), mask=blue)
            image.paste(hero, (40, add+(x*rng)), mask=glow)
            draw.text((155, add+(x*rng)+30), name, (105,156,249), font=name_font)
            color = (105,156,249)
            postfix = 'blue'

        else:
            image.paste(rplayer, (25, add+(x*rng)), mask=rplayer)
            image.paste(red, (25+rplayer.size[0], add+(x*rng)), mask=red)
            image.paste(hero, (40, add+(x*rng)), mask=glow)
            draw.text((155, add+(x*rng)+30), name, (234,140,140), font=name_font)
            color = (234,140,140)
            postfix = 'red'

        hero_short_name = hots.htts_data.get_short_hero(player.hero)

        draw.text((155, add+(x*rng)+10), hero_short_name, (255,255,255), font=hots.config.vs_font)

        for mvp in hots.visual.mvps:
            if getattr(player, 'award_'+mvp):
                tmp = Image.open(hots.config.vs_mvp_path+f'{hots.visual.mvps[mvp]}_{postfix}.png')
                tmp = tmp.resize((48, 48))
                image.paste(tmp, (270, add+(x*rng)+4), mask=tmp)

        solo_kill = str(player.solo_kill)
        shift = get_shift(solo_kill)
        draw.text((340-shift, add+(x*rng)+20), solo_kill, color, font=hots.config.vs_font)

        assists = str(player.assists)
        shift = get_shift(assists)
        draw.text((400-shift, add+(x*rng)+20), assists, color, font=hots.config.vs_font)

        deaths = str(player.deaths)
        shift = get_shift(deaths)
        draw.text((460-shift, add+(x*rng)+20), deaths, color, font=hots.config.vs_font)

        structure_damage = str(player.structure_damage)
        shift = get_shift(structure_damage)
        if id in max_stats[team_id]['structure_damage'][0]:
            draw.text((560-shift, add+(x*rng)+20), structure_damage, (255, 255, 255), font=hots.config.vs_font)
        else:
            draw.text((560-shift, add+(x*rng)+20), structure_damage, color, font=hots.config.vs_font)

        minion_damage = str(player.minion_damage)
        shift = get_shift(minion_damage)
        if id in max_stats[team_id]['minion_damage'][0]:
            draw.text((660-shift, add+(x*rng)+20), minion_damage, (255, 255, 255), font=hots.config.vs_font)
        else:
            draw.text((660-shift, add+(x*rng)+20), minion_damage, color, font=hots.config.vs_font)

        hero_damage = str(player.hero_damage)
        shift = get_shift(hero_damage)
        if id in max_stats[team_id]['hero_damage'][0]:
            draw.text((760-shift, add+(x*rng)+20), hero_damage, (255, 255, 255), font=hots.config.vs_font)
        else:
            draw.text((760-shift, add+(x*rng)+20), hero_damage, color, font=hots.config.vs_font)

        taken_damage = str(player.taken_damage)
        shift = get_shift(taken_damage)
        if id in max_stats[team_id]['taken_damage'][0]:
            draw.text((860-shift, add+(x*rng)+20), taken_damage, (255, 255, 255), font=hots.config.vs_font)
        else:
            draw.text((860-shift, add+(x*rng)+20), taken_damage, color, font=hots.config.vs_font)

        healing = str(player.healing)
        shift = get_shift(healing)
        if healing == '0': healing = '-'
        if id in max_stats[team_id]['healing'][0]:
            draw.text((960-shift, add+(x*rng)+20), healing, (255, 255, 255), font=hots.config.vs_font)
        else:
            draw.text((960-shift, add+(x*rng)+20), healing, color, font=hots.config.vs_font)

        self_healing = str(player.self_healing)
        shift = get_shift(self_healing)
        if self_healing == '0': self_healing = '-'
        if id in max_stats[team_id]['self_healing'][0]:
            draw.text((1060-shift, add+(x*rng)+20), self_healing, (255, 255, 255), font=hots.config.vs_font)
        else:
            draw.text((1060-shift, add+(x*rng)+20), self_healing, color, font=hots.config.vs_font)

        merc_camps = str(player.merc_camps)
        shift = get_shift(merc_camps)
        if merc_camps == '0': merc_camps = '-'
        if id in max_stats[team_id]['merc_camps'][0]:
            draw.text((1160-shift, add+(x*rng)+20), merc_camps, (255, 255, 255), font=hots.config.vs_font)
        else:
            draw.text((1160-shift, add+(x*rng)+20), merc_camps, color, font=hots.config.vs_font)

        experience = str(player.experience)
        shift = get_shift(experience)
        if id in max_stats[team_id]['experience'][0]:
            draw.text((1260-shift, add+(x*rng)+20), experience, (255, 255, 255), font=hots.config.vs_font)
        else:
            draw.text((1260-shift, add+(x*rng)+20), experience, color, font=hots.config.vs_font)


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
    redkills = Image.open(hots.config.vs_stats_path+'redkills.png')
    bluekills = Image.open(hots.config.vs_stats_path+'bluekills.png')
    language = hots.language

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

    draw.text(coords, hots.strings['ImageBlueTeam'], (185,213,255), font=hots.config.vs_large_font)
    draw.text((105, 740), hots.strings('ImageLevelTeam', blue_level), (39,153,165), font=hots.config.vs_large_font)
    draw.text((290, 715), str(blue_kills), (185,213,255), font=hots.config.vs_big_font)
    image.paste(bluekills, (360, 725), mask=bluekills)

    draw.text((1350-250, 710), hots.strings['ImageRedTeam'], (234,140,140), font=hots.config.vs_large_font)
    draw.text((1350-250, 740), hots.strings('ImageLevelTeam', red_level), (175,76,105), font=hots.config.vs_large_font)
    draw.text((1350-330, 715), str(red_kills), (185,213,255), font=hots.config.vs_big_font)
    image.paste(redkills, (1350-390, 725), mask=redkills)

    if language == 'ru':
        coords = (550, 720)
    else:
        coords = (580, 720)

    draw.text(coords, hots.strings['ImageMatchDuration'], (138,166,251), font=hots.config.vs_large_font)
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
    image.save(hots.config.vs_screens_path + _name)

    hots.print_log('ImageUploadMatch')
    url = hots.visual.upload.upload_file(hots.config.vs_screens_path + _name, _name)

    return url
