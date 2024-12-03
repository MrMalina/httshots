# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
import asyncio
import hashlib
import os
import time

# httshots
import httshots
from httshots import httshots


# ======================================================================
# >> Functions
# ======================================================================
async def send_battle_lobby_info(pre_game):
    info = pre_game.players

    # 24-11-28 20-22
    httshots.cur_game[0] = time.strftime('%y-%m-%d')
    httshots.cur_game[1] = time.strftime('%H-%M')

    url = httshots.visual.battlelobby.create_image(info)
    text = httshots.strings['LobbyInfo'].format(url)
    
    pre_game.url = url

    httshots.stream_pregame.append(pre_game)

    await httshots.tw_bot.channel.send(text)


async def check_battle_lobby():
    # try:
    if os.path.isfile(httshots.battle_lobby_file):
        file = open(httshots.battle_lobby_file, 'rb')
        contents = file.read()
        file.close()
        hash = hashlib.md5(contents).hexdigest()
        if httshots.battle_lobby_hash is None or httshots.battle_lobby_hash != hash:
            httshots.battle_lobby_hash = hash
            pre_game = httshots.parser.get_battle_lobby(contents)
            loop = asyncio.get_event_loop()
            task = loop.create_task(httshots.bot.tracker.start_check_talents())
            httshots.check_talents_task = task
            await send_battle_lobby_info(pre_game)

    # except Exception as e:
        # print('Oooooops', e)
