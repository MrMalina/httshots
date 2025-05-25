# ======================================================================
# >> IMPORTS
# ======================================================================

# python
from PIL import Image
from PIL import ImageDraw

# httshots
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
    return Image.open(hots.paths.bg / 'clear_background.png')


def create_icons(image, map_name):
    map_number = int(hots.htts_data.maps.get(map_name.lower(), -1))

    y = 50

    # Физический урон
    tmp = Image.open(hots.paths.stats / 'adv_ad_damage.png').convert('RGBA')
    image.paste(tmp, (340, y), mask=tmp)

    # Магический урон
    tmp = Image.open(hots.paths.stats / 'adv_ap_damage.png').convert('RGBA')
    image.paste(tmp, (440, y), mask=tmp)

    # Длительность оглушения
    tmp = Image.open(hots.paths.stats / 'adv_stunner.png').convert('RGBA')
    image.paste(tmp, (540, y), mask=tmp)

    # Длительность обездвижевания
    tmp = Image.open(hots.paths.stats / 'adv_trapper.png').convert('RGBA')
    image.paste(tmp, (640, y), mask=tmp)

    # Длительность молчания
    tmp = Image.open(hots.paths.stats / 'adv_silencer.png').convert('RGBA')
    image.paste(tmp, (740, y), mask=tmp)

    # Длительность смерти
    tmp = Image.open(hots.paths.stats / 'adv_death.png').convert('RGBA')
    image.paste(tmp, (840, y), mask=tmp)

    # Стрик из убийств
    tmp = Image.open(hots.paths.stats / 'adv_scrapper.png').convert('RGBA')
    image.paste(tmp, (940, y), mask=tmp)

    # Поднято сфер
    tmp = Image.open(hots.paths.stats / 'adv_globes.png').convert('RGBA')
    image.paste(tmp, (1040, y), mask=tmp)

    # Альтеракский перевал = 1
    # Небесный храм = 2
    # Вечная битва = 3
    # Гробница Королевы Пауков = 4
    # Драконий край = 5
    # Проклятая лощина = 6
    # Башни Рока = 7
    # Завод Вольской = 8
    # Храм Ханамура = 9
    # Бойня на Браксисе = 10
    # Призрачные копи = 11
    # Оскверненные святилища = 12
    # Ядерный полигон = 13
    # Бухта Черносерда = 14
    # Сад ужасов = 15

    if map_number in (-1, 1, 8, 15):
        # На Альтераке, садах и вольской
        return
    if map_number == 2:
        img_name = 'adv_templemaster.png'
        stat = 'time_in_temple'
    elif map_number == 3:
        img_name = 'adv_immortalslayer.png'
        stat = 'immortal_damage'
    elif map_number == 4:
        img_name = 'adv_jeweler.png'
        stat = 'gems'
    elif map_number == 5:
        img_name = 'adv_shriner.png'
        # stat = 'dragon_shrines_captured'
        stat = 'dragons'
    elif map_number == 6:
        img_name = 'adv_masterofthecurse.png'
        stat = 'curse_damage'
    elif map_number == 7:
        img_name = 'adv_cannoneer.png'
        stat = 'altar_damage'
    elif map_number == 8:
        img_name = 'adv_pointguard.png'
        stat = 'dragons'
    elif map_number == 9:
        img_name = 'adv_pointguard.png'
        stat = 'time_on_payload'
    elif map_number == 10:
        img_name = 'adv_zergcrusher.png'
        stat = 'zerg_damage'
    elif map_number == 11:
        img_name = 'adv_skullcollector.png'
    elif map_number == 12:
        img_name = 'adv_skull.png'
        stat = 'damage_to_shrine_minions'
    elif map_number == 13:
        img_name = 'adv_dabomb.png'
        stat = 'nuke_damage'
    elif map_number == 14:
        img_name = 'adv_moneybags.png'
        stat = 'doubloons_turned_in'
    elif map_number == 15:
        img_name = 'adv_gardenterror.png'
        stat = 'plant_damage'

    tmp = Image.open(hots.paths.stats / img_name).convert('RGBA')
    image.paste(tmp, (1140, y), mask=tmp)

    return stat


def get_max_stats(replay, map_stat):
    max_stats = {0: {}, 1: {}}
    stats = ['physical_damage', 'spell_damage', 'stunning_time', 'rooting_time', 'silencing_time',
             'death_time', 'kill_streak', 'globes']

    if map_stat:
        stats.append(map_stat)

    for stat in stats:
        max_stats[0][stat] = 0
        max_stats[1][stat] = 0

        for player in replay.players.values():
            value = getattr(player, stat)
            team_id = player.team_id
            _id = player.userid
            if not max_stats[team_id][stat]:
                max_stats[team_id][stat] = [[_id], value]
                continue

            if value > max_stats[team_id][stat][1]:
                max_stats[team_id][stat] = [[_id], value]

            elif value == max_stats[team_id][stat][1]:
                max_stats[team_id][stat][0].append(_id)

    return max_stats


def add_heroes(image, replay, max_stats, map_stat):
    blue = Image.open(hots.paths.score / 'blue.png')
    bplayer = Image.open(hots.paths.score / 'playerblue.png').convert('RGBA')
    red = Image.open(hots.paths.score / 'red.png')
    rplayer = Image.open(hots.paths.score / 'playerred.png').convert('RGBA')
    glow = Image.open(hots.paths.score / 'portrait.png').convert('RGBA')

    add = 120
    rng = 60

    stats = ['physical_damage', 'spell_damage', 'stunning_time', 'rooting_time', 'silencing_time',
             'death_time', 'kill_streak', 'globes']

    if map_stat:
        stats.append(map_stat)

    for y, player in enumerate(replay.players.values()):
        hero_name = hots.htts_data.get_eng_hero(player.hero)
        hero = Image.open(hots.paths.heroes / (hero_name.lower() + '.png')).convert('RGBA')

        draw = ImageDraw.Draw(image)

        team_id = player.team_id
        _id = player.userid

        name = player.name
        check = hots.visual.check_name.match(name)[0]
        if check:
            name_font = hots.fonts.default
        else:
            name_font = hots.fonts.ch_default

        if team_id == 0:
            image.paste(bplayer, (25, add+(y*rng)), mask=bplayer)
            image.paste(blue, (25+rplayer.size[0], add+(y*rng)), mask=blue)
            image.paste(hero, (40, add+(y*rng)), mask=glow)
            draw.text((155, add+(y*rng)+30), name, BTEAM, font=name_font)
            color = BTEAM

        else:
            image.paste(rplayer, (25, add+(y*rng)), mask=rplayer)
            image.paste(red, (25+rplayer.size[0], add+(y*rng)), mask=red)
            image.paste(hero, (40, add+(y*rng)), mask=glow)
            draw.text((155, add+(y*rng)+30), name, RTEAM, font=name_font)
            color = RTEAM

        hero_short_name = hots.htts_data.get_short_hero(player.hero)

        draw.text((155, add+(y*rng)+10), hero_short_name, WHITE, font=hots.fonts.default)

        x = 360
        for stat in stats:
            value = str(getattr(player, stat))
            shift = get_shift(value)
            if _id in max_stats[team_id][stat][0]:
                draw.text((x-shift, add+(y*rng)+20), value, WHITE, font=hots.fonts.default)
            else:
                draw.text((x-shift, add+(y*rng)+20), value, color, font=hots.fonts.default)

            x+=100


def get_shift(value):
    ln = len(value)
    if ln == 6:
        return 11.5
    if ln == 5:
        return 8
    if ln == 4:
        return 3
    if ln == 3:
        return -4
    if ln == 2:
        return -7
    if ln == 1:
        return -11

    return 0


def create_image(replay):
    _name = 'match_adv.png'

    hots.print_log('ImageStartCreateMatchAdvImage', level=0)
    hots.print_log('ImageLoadBackGround', level=0)
    image = load_background()

    hots.print_log('ImageCreateIcons', level=0)
    map_stat = create_icons(image, replay.details.title)

    hots.print_log('ImageGetMaxStats', level=0)
    max_stats = get_max_stats(replay, map_stat)

    hots.print_log('ImageAddHeroes', level=0)
    add_heroes(image, replay, max_stats, map_stat)

    hots.print_log('ImageSaveImageMatch', level=0)
    image.save(hots.paths.upload / _name)

    hots.print_log('ImageUploadMatchAdv', level=2)
    url = hots.visual.upload.upload_file(hots.paths.upload / _name, _name)
    if hots.config.duplicate_url_in_console:
        hots.print_log('SendUrl', url, level=3)
    return url
