# ======================================================================
# >> IMPORTS
# ======================================================================

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

import httshots
from httshots import httshots as hots


# ======================================================================
# >> FUNCTIONS
# ======================================================================
def load_background():
    return Image.open(hots.config.vs_bg_path+'lobby_background.png')


def add_users(image, info):
    partys = []

    add = 20
    rng = 60

    vc_party1 = Image.open(hots.config.vs_stats_path+'vc_party1.png')
    vc_party2 = Image.open(hots.config.vs_stats_path+'vc_party2.png')
    vc_party3 = Image.open(hots.config.vs_stats_path+'vc_party3.png')
    vc_party4 = Image.open(hots.config.vs_stats_path+'vc_party4.png')

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
                image.paste(icon, (250, add+(x*rng)-15), mask=icon)

        else:
            coords = 420
            coords2 = 370
            x -= 5

            if party:
                icon = icons[partys.index(party)]
                image.paste(icon, (310, add+(x*rng)-15), mask=icon)

        draw.text((coords2, add+(x*rng)+3), "(%s)"%blplayer.level, (255,255,255), font=hots.config.vs_small_font)
        draw.text((coords, add+(x*rng)+3), blplayer.battle_tag, (255,255,255), font=hots.config.vs_small_font)


def create_image(info):
    _name = 'battlelobby.png'
    hots.print_log('ImageStartCreateLobbyImage', uwaga=0)
    image = load_background()

    hots.print_log('ImageAddUsers', uwaga=0)
    add_users(image, info)

    hots.print_log('ImageSaveImageMatch', uwaga=0)
    image.save(hots.config.vs_screens_path + _name)

    hots.print_log('ImageUploadBattleLobby')
    url = hots.visual.upload.upload_image(hots.config.vs_screens_path + _name, _name)

    return url
