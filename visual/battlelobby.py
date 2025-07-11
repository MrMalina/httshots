# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
from PIL import Image
from PIL import ImageDraw

# httshots
from httshots import httshots as hots


# ======================================================================
# >> CONSTS
# ======================================================================
WHITE = (255,255,255)

# ======================================================================
# >> FUNCTIONS
# ======================================================================
def load_background():
    return Image.open(hots.paths.bg / 'lobby_background.png')


def add_users(image, info):
    partys = []

    add = 20
    rng = 60

    vc_party1 = Image.open(hots.paths.stats / 'vc_party1.png')
    vc_party2 = Image.open(hots.paths.stats / 'vc_party2.png')
    vc_party3 = Image.open(hots.paths.stats / 'vc_party3.png')
    vc_party4 = Image.open(hots.paths.stats / 'vc_party4.png')

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

        btag = blplayer.battle_tag
        name = hots.visual.check_name.match(btag)[0]
        if name:
            name_font = hots.fonts.small
        else:
            name_font = hots.fonts.ch_small

        draw.text((coords2, add+(x*rng)+3), "(%s)"%blplayer.level, WHITE, font=hots.fonts.small)
        draw.text((coords, add+(x*rng)+3), btag, WHITE, font=name_font)


def create_image(info):
    _name = 'lobby.png'
    hots.print_log('ImageStartCreateLobbyImage', level=0)
    image = load_background()

    hots.print_log('ImageAddUsers', level=0)
    add_users(image, info)

    hots.print_log('ImageSaveImageMatch', level=0)
    image.save(hots.paths.upload / _name)

    hots.print_log('ImageUploadBattleLobby', level=2)
    url = hots.visual.upload.upload_file(hots.paths.upload / _name, _name)
    if hots.config.duplicate_url_in_console:
        hots.print_log('SendUrl', url, level=3)
    return url
