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

    httshots.print_log('NewGame', level=3)
    upload = httshots.config.image_upload
    url = httshots.visual.battlelobby.create_image(info, 1 & upload)
    if url:
        text = httshots.strings['LobbyInfo'].format(url)

        pre_game.url = url
        httshots.stream_pregame.append(pre_game)
        await httshots.tw_bot.send_chat_message(text)


    pre_game.url = None
    httshots.bot.events.match_start()

    if 2 & upload:
        await httshots.ds_bot.send_chat_message('battlelobby', 'battlelobby.png')


async def check_battle_lobby():
    # try:
    if os.path.isfile(httshots.config.battle_lobby_file):
        file = open(httshots.config.battle_lobby_file, 'rb')
        contents = file.read()
        file.close()
        _hash = hashlib.md5(contents).hexdigest()
        if httshots.battle_lobby_hash is None or httshots.battle_lobby_hash != _hash:
            httshots.battle_lobby_hash = _hash
            pre_game = httshots.parser.get_battle_lobby(contents)

            # При обработке battlelobby была ошибка
            if pre_game is not None:
                # Работает только для FTP
                if httshots.config.image_upload and httshots.config.tracker_status == 1:
                    # Запуск отслеживания выбранных талантов
                    loop = asyncio.get_event_loop()
                    task = loop.create_task(httshots.bot.tracker.start_check_talents())
                    # Для выключения задачи после окончания матча
                    httshots.check_talents_task = task

                await send_battle_lobby_info(pre_game)

    # except Exception as e:
        # print('Oooooops', e)
