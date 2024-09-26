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
bg_files = path + "background/"
font_files = path + "ttf/"
screens_files = path + "screens/"
stats_files = path + "stats/"
small_font = ImageFont.truetype(font_files+'Exo2-Bold.ttf', 12)
font = ImageFont.truetype(font_files+'Exo2-Bold.ttf', 16)


# ======================================================================
# >> FUNCTIONS
# ======================================================================
def load_background():
    return Image.open(bg_files+'lobby_background.png')


def add_users(image, info):
    partys = []

    add = 20
    rng = 60

    vc_party1 = Image.open(stats_files+'vc_party1.png')
    vc_party2 = Image.open(stats_files+'vc_party2.png')
    vc_party3 = Image.open(stats_files+'vc_party3.png')
    vc_party4 = Image.open(stats_files+'vc_party4.png')

    icons = [vc_party1, vc_party2, vc_party3, vc_party4]

    for x, blplayer in enumerate(info):
        draw = ImageDraw.Draw(image)

        party = blplayer.party

        if party != 0 and not party in partys:
            partys.append(party)

        if blplayer.userid < 5:
            coords = 10
            coords2 = 200
            if party:
                icon = icons[partys.index(party)]
                image.paste(icon, (240, add+(x*rng)-15), mask=icon)

        else:
            coords = 410
            coords2 = 360
            x -= 5

            if party:
                icon = icons[partys.index(party)]
                image.paste(icon, (300, add+(x*rng)-15), mask=icon)

        draw.text((coords2, add+(x*rng)+3), "(%s)"%blplayer.level, (255,255,255), font=small_font)
        draw.text((coords, add+(x*rng)), blplayer.battle_tag, (255,255,255), font=font)


def upload_image():
    try:
        url = httshots.imgur.upload_from_path(screens_files + 'vavaviva_battlelobby.png')
        if 'link' in url:
            return url['link'].replace('i.', '')
        return None
    except Exception as e:
        print(e)
        return None


def create_image(info):
    httshots.print_log('ImgurStartCreateLobbyImage', 1)
    image = load_background()

    httshots.print_log('ImgurAddUsers', 1)
    add_users(image, info)

    httshots.print_log('ImgurSaveImageMatch', 1)
    image.save(screens_files + 'vavaviva_battlelobby.png')

    httshots.print_log('ImgurUploadImageMatch', 1)
    url = upload_image()

    return url
