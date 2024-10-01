# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
import asyncio
import hashlib
import os

# httshots
import httshots
from httshots import httshots


# ======================================================================
# >> Functions
# ======================================================================
async def send_battle_lobby_info(pre_game):
    info = pre_game.players

    url = httshots.score.battlelobby.create_image(info)
    text = httshots.strings['LobbyInfo'].format(url)
    
    pre_game.url = url

    httshots.stream_pregame.append(pre_game)

    await httshots.bot.channel.send(text)


async def check_battle_lobby():
    try:
        if os.path.isfile(httshots.battle_lobby_file):
            file = open(httshots.battle_lobby_file, 'rb')
            contents = file.read()
            file.close()
            hash = hashlib.md5(contents).hexdigest()
            if httshots.battle_lobby_hash is None or httshots.battle_lobby_hash != hash:
                httshots.battle_lobby_hash = hash
                pre_game = httshots.parser.get_battle_lobby(contents)
                await send_battle_lobby_info(pre_game)
    except Exception as e:
        print('Oooooops', e)
