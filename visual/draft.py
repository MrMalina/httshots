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
BTEAM = (105,156,249)
RTEAM = (234,140,140)


# ======================================================================
# >> FUNCTIONS
# ======================================================================
def load_background():
    return Image.open(hots.paths.bg / 'draft_background.png')


def add_bans_and_picks(image, info):
    # Draft order
    # 1. BAN TEAM1, 2. BAN TEAM2
    # 3. BAN TEAM1, 4. BAN TEAM2
    # 5. PICK TEAM1
    # 6. PICK TEAM2, 7. PICK TEAM2
    # 8. PICK TEAM1, 9. PICK TEAM1
    # 10. BAN TEAM2, 11. BAN TEAM1
    # 12. PICK TEAM2, 13. PICK TEAM2
    # 14. PICK TEAM1, 15. PICK TEAM1
    # 16. PICK TEAM2

    ban_frame = Image.open(hots.paths.utils / 'draft_ban_frame_normal.png').convert('RGBA')
    ban_icon = Image.open(hots.paths.utils / 'draft_ban_lock_normal.png').convert('RGBA')
    draft_frame = Image.open(hots.paths.utils / 'draft_portrait_selected.png').convert('RGBA')
    draft_frame = draft_frame.resize((135, 148))

    # ??????
    x = 50
    shift_x = 120
    y = [50, 370]

    frame_shift = (-31, -28)
    icon_shift = (21, 65)

    bans = info.lobby.bans
    picks = info.lobby.picks

    # 1. BAN TEAM 1
    name = bans[0].hero
    img_name = 'draft_' + name.lower() + '.png'
    hero = Image.open(hots.paths.heroes / img_name).convert('RGBA')
    if name == 'skipban':
        image.paste(hero, (x-50, y[0]-50), mask=hero)
    else:
        rx, ry = x+frame_shift[0], y[0]+frame_shift[1]
        hero = hero.resize((80, 94))
        image.paste(hero, (x, y[0]), mask=hero)
        image.paste(ban_frame, (rx, ry), mask=ban_frame)

    rx, ry = x+icon_shift[0], y[0]+icon_shift[1]
    image.paste(ban_icon, (rx, ry), mask=ban_icon)

    # 2. BAN TEAM 2
    name = bans[1].hero
    img_name = 'draft_' + name.lower() + '.png'
    hero = Image.open(hots.paths.heroes / img_name).convert('RGBA')
    if name == 'skipban':
        image.paste(hero, (x-50, y[1]-50), mask=hero)
    else:
        rx, ry = x+frame_shift[0], y[1]+frame_shift[1]
        hero = hero.resize((80, 94))
        image.paste(hero, (x, y[1]), mask=hero)
        image.paste(ban_frame, (rx, ry), mask=ban_frame)

    rx, ry = x+icon_shift[0], y[1]+icon_shift[1]
    image.paste(ban_icon, (rx, ry), mask=ban_icon)

    # 3. BAN TEAM 1
    x += shift_x
    name = bans[2].hero
    img_name = 'draft_' + name.lower() + '.png'
    hero = Image.open(hots.paths.heroes / img_name).convert('RGBA')
    if name == 'skipban':
        image.paste(hero, (x-50, y[0]-50), mask=hero)
    else:
        rx, ry = x+frame_shift[0], y[0]+frame_shift[1]
        hero = hero.resize((80, 94))
        image.paste(hero, (x, y[0]), mask=hero)
        image.paste(ban_frame, (rx, ry), mask=ban_frame)

    rx, ry = x+icon_shift[0], y[0]+icon_shift[1]
    image.paste(ban_icon, (rx, ry), mask=ban_icon)

    # 4. BAN TEAM 2
    name = bans[3].hero
    img_name = 'draft_' + name.lower() + '.png'
    hero = Image.open(hots.paths.heroes / img_name).convert('RGBA')
    if name == 'skipban':
        image.paste(hero, (x-50, y[1]-50), mask=hero)
    else:
        rx, ry = x+frame_shift[0], y[1]+frame_shift[1]
        hero = hero.resize((80, 94))
        image.paste(hero, (x, y[1]), mask=hero)
        image.paste(ban_frame, (rx, ry), mask=ban_frame)

    rx, ry = x+icon_shift[0], y[1]+icon_shift[1]
    image.paste(ban_icon, (rx, ry), mask=ban_icon)

    # 5. PICK TEAM 1
    x += shift_x

    name = picks[0].hero
    img_name = 'draft_' + name.lower() + '.png'
    hero = Image.open(hots.paths.heroes / img_name).convert('RGBA')
    hero = hero.resize((100, 117))
    image.paste(hero, (x, y[0]-16), mask=hero)
    image.paste(draft_frame, (x-17, y[0]-32), mask=draft_frame)

    # 6. PICK TEAM 2
    name = picks[1].hero
    img_name = 'draft_' + name.lower() + '.png'
    hero = Image.open(hots.paths.heroes / img_name).convert('RGBA')
    hero = hero.resize((100, 117))
    image.paste(hero, (x, y[1]-16), mask=hero)
    image.paste(draft_frame, (x-17, y[1]-32), mask=draft_frame)

    # 7. PICK TEAM 2
    x += shift_x + 10

    name = picks[2].hero
    img_name = 'draft_' + name.lower() + '.png'
    hero = Image.open(hots.paths.heroes / img_name).convert('RGBA')
    hero = hero.resize((100, 117))
    image.paste(hero, (x, y[1]-16), mask=hero)
    image.paste(draft_frame, (x-17, y[1]-32), mask=draft_frame)

    # 8. PICK TEAM 1
    name = picks[3].hero
    img_name = 'draft_' + name.lower() + '.png'
    hero = Image.open(hots.paths.heroes / img_name).convert('RGBA')
    hero = hero.resize((100, 117))
    image.paste(hero, (x, y[0]-16), mask=hero)
    image.paste(draft_frame, (x-17, y[0]-32), mask=draft_frame)

    # 9. PICK TEAM 1
    x += shift_x + 10

    name = picks[4].hero
    img_name = 'draft_' + name.lower() + '.png'
    hero = Image.open(hots.paths.heroes / img_name).convert('RGBA')
    hero = hero.resize((100, 117))
    image.paste(hero, (x, y[0]-16), mask=hero)
    image.paste(draft_frame, (x-17, y[0]-32), mask=draft_frame)

    # 10. BAN TEAM 2
    x += 10
    name = bans[4].hero
    img_name = 'draft_' + name.lower() + '.png'
    hero = Image.open(hots.paths.heroes / img_name).convert('RGBA')
    if name == 'skipban':
        image.paste(hero, (x-50, y[1]-50), mask=hero)
    else:
        rx, ry = x+frame_shift[0], y[1]+frame_shift[1]
        hero = hero.resize((80, 94))
        image.paste(hero, (x, y[1]), mask=hero)
        image.paste(ban_frame, (rx, ry), mask=ban_frame)

    rx, ry = x+icon_shift[0], y[1]+icon_shift[1]
    image.paste(ban_icon, (rx, ry), mask=ban_icon)

    # 11. BAN TEAM 1
    x += shift_x + 10
    name = bans[5].hero
    img_name = 'draft_' + name.lower() + '.png'
    hero = Image.open(hots.paths.heroes / img_name).convert('RGBA')
    if name == 'skipban':
        image.paste(hero, (x-50, y[0]-50), mask=hero)
    else:
        rx, ry = x+frame_shift[0], y[0]+frame_shift[1]
        hero = hero.resize((80, 94))
        image.paste(hero, (x, y[0]), mask=hero)
        image.paste(ban_frame, (rx, ry), mask=ban_frame)

    rx, ry = x+icon_shift[0], y[0]+icon_shift[1]
    image.paste(ban_icon, (rx, ry), mask=ban_icon)

    # 12. PICK TEAM 2
    x -= 10
    name = picks[5].hero
    img_name = 'draft_' + name.lower() + '.png'
    hero = Image.open(hots.paths.heroes / img_name).convert('RGBA')
    hero = hero.resize((100, 117))
    image.paste(hero, (x, y[1]-16), mask=hero)
    image.paste(draft_frame, (x-17, y[1]-32), mask=draft_frame)

    # 13. PICK TEAM 2
    x += shift_x + 10

    name = picks[6].hero
    img_name = 'draft_' + name.lower() + '.png'
    hero = Image.open(hots.paths.heroes / img_name).convert('RGBA')
    hero = hero.resize((100, 117))
    image.paste(hero, (x, y[1]-16), mask=hero)
    image.paste(draft_frame, (x-17, y[1]-32), mask=draft_frame)

    # 14. PICK TEAM 1
    name = picks[7].hero
    img_name = 'draft_' + name.lower() + '.png'
    hero = Image.open(hots.paths.heroes / img_name).convert('RGBA')
    hero = hero.resize((100, 117))
    image.paste(hero, (x, y[0]-16), mask=hero)
    image.paste(draft_frame, (x-17, y[0]-32), mask=draft_frame)

    # 15. PICK TEAM 1
    x += shift_x + 10
    name = picks[8].hero
    img_name = 'draft_' + name.lower() + '.png'
    hero = Image.open(hots.paths.heroes / img_name).convert('RGBA')
    hero = hero.resize((100, 117))
    image.paste(hero, (x, y[0]-16), mask=hero)
    image.paste(draft_frame, (x-17, y[0]-32), mask=draft_frame)

    # 16. PICK TEAM 2
    name = picks[9].hero
    img_name = 'draft_' + name.lower() + '.png'
    hero = Image.open(hots.paths.heroes / img_name).convert('RGBA')
    hero = hero.resize((100, 117))
    image.paste(hero, (x, y[1]-16), mask=hero)
    image.paste(draft_frame, (x-17, y[1]-32), mask=draft_frame)

    return image


def add_others(image, info):
    draw = ImageDraw.Draw(image)

    x = 90
    x_shift = 120
    y_text = 247
    y = [150, 360]

    if info.lobby.bans[0].team == 1:
        colors = [BTEAM, RTEAM]
    else:
        colors = [RTEAM, BTEAM]

    # 1. BAN TEAM 1
    rx = x - 30
    draw.line((rx+3, 245, rx+3, y[0]), fill=colors[0], width = 2)
    draw.text((rx, y_text), '1', fill=colors[0], font=hots.fonts.default)

    # 2. BAN TEAM 2
    rx = x + 30 - 4
    draw.line((rx+4, 270, rx+4, y[1]), fill=colors[1], width = 2)
    draw.text((rx, y_text), '2', fill=colors[1], font=hots.fonts.default)

    # 3. BAN TEAM 1
    x += x_shift
    rx = x - 30
    draw.line((rx+3, 245, rx+3, y[0]), fill=colors[0], width = 2)
    draw.text((rx, y_text), '3', fill=colors[0], font=hots.fonts.default)

    # 4. BAN TEAM 2
    rx = x + 30 - 4
    draw.line((rx+4, 270, rx+4, y[1]), fill=colors[1], width = 2)
    draw.text((rx, y_text), '4', fill=colors[1], font=hots.fonts.default)

    # 5. PICK TEAM 1
    x += x_shift + 6
    rx = x - 30
    draw.line((rx+3, 245, rx+3, y[0]), fill=colors[0], width = 2)
    draw.text((rx, y_text), '5', fill=colors[0], font=hots.fonts.default)

    # 6. PICK TEAM 2
    rx = x + 30
    draw.line((rx+4, 270, rx+4, y[1]), fill=colors[1], width = 2)
    draw.text((rx, y_text), '6', fill=colors[1], font=hots.fonts.default)

    # 7. PICK TEAM 2
    x += x_shift + 10
    rx = x - 30
    draw.line((rx+4, 270, rx+4, y[1]), fill=colors[1], width = 2)
    draw.text((rx, y_text), '7', fill=colors[1], font=hots.fonts.default)

    # 8. PICK TEAM 1
    rx = x + 30
    draw.line((rx+4, 245, rx+4, y[0]), fill=colors[0], width = 2)
    draw.text((rx, y_text), '8', fill=colors[0], font=hots.fonts.default)

    # 9. PICK TEAM 1
    x += x_shift + 7
    rx = x - 30
    draw.line((rx+4, 245, rx+4, y[0]), fill=colors[0], width = 2)
    draw.text((rx, y_text), '9', fill=colors[0], font=hots.fonts.default)

    # 10. BAN TEAM 2
    rx = x + 30 - 4
    draw.line((rx+7, 270, rx+7, y[1]), fill=colors[1], width = 2)
    draw.text((rx, y_text), '10', fill=colors[1], font=hots.fonts.default)

    # 11. BAN TEAM 1
    x += x_shift + 7
    rx = x - 30
    draw.line((rx+7, 245, rx+7, y[0]), fill=colors[0], width = 2)
    draw.text((rx, y_text), '11', fill=colors[0], font=hots.fonts.default)

    # 12. PICK TEAM 2
    rx = x + 30
    draw.line((rx+7, 270, rx+7, y[1]), fill=colors[1], width = 2)
    draw.text((rx,y_text), '12', fill=colors[1], font=hots.fonts.default)

    # 13. PICK TEAM 2
    x += x_shift + 12
    rx = x - 30
    draw.line((rx+7, 270, rx+7, y[1]), fill=colors[1], width = 2)
    draw.text((rx, y_text), '13', fill=colors[1], font=hots.fonts.default)

    # 14. PICK TEAM 1
    rx = x + 30
    draw.line((rx+7, 245, rx+7, y[0]), fill=colors[0], width = 2)
    draw.text((rx, y_text), '14', fill=colors[0], font=hots.fonts.default)

    # 15. PICK TEAM 1
    x += x_shift + 12
    rx = x - 30
    draw.line((rx+7, 245, rx+7, y[0]), fill=colors[0], width = 2)
    draw.text((rx, y_text), '15', fill=colors[0], font=hots.fonts.default)

    # 16. PICK TEAM 2
    rx = x + 30
    draw.line((rx+7, 270, rx+7, y[1]), fill=colors[1], width = 2)
    draw.text((rx, y_text), '16', fill=colors[1], font=hots.fonts.default)

    return image


def create_image(replay):
    _name = 'draft.png'
    hots.print_log('ImageStartCreateDraftImage', level=0)
    hots.print_log('ImageLoadBackGround', level=0)
    image = load_background()

    hots.print_log('ImageAddBansAndPicks', level=0)
    add_bans_and_picks(image, replay)

    hots.print_log('ImageAddLinesAndNumbers', level=0)
    add_others(image, replay)

    hots.print_log('ImageSaveImageMatch', level=0)
    image.save(hots.paths.upload / _name)

    hots.print_log('ImageUploadDraft', level=2)
    url = hots.visual.upload.upload_file(hots.paths.upload / _name, _name)
    if hots.config.duplicate_url_in_console:
        hots.print_log('SendUrl', url, level=3)

    return url
