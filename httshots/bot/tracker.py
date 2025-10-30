# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
import asyncio
import copy
import hashlib
import os
from twitchio.ext import commands

# httshots
import httshots
from httshots import httshots


# ======================================================================
# >> Functions
# ======================================================================
old_talents = None

async def start_check_talents():
    global old_talents
    while True:
        with open(httshots.config.tracker_events_file, 'rb') as f:
            contents = f.read()
        _hash = hashlib.md5(contents).hexdigest()

        if httshots.tracker_events_hash != _hash:
            httshots.tracker_events_hash = _hash

            if not len(httshots.stream_pregame):
                with open(httshots.config.battle_lobby_file, 'rb') as f:
                    _contents = f.read()
                pre_game = httshots.parser.get_battle_lobby(_contents)
            else:
                pre_game = httshots.stream_pregame[-1]

            # Возможно, излишне
            try:
                _talents = httshots.parser.ingame.parse_content(contents, pre_game)
                if httshots.config.debug:
                    print(_talents, old_talents)
                if _talents:
                    # Нет смысла генерировать изображение, если таланты не поменялись
                    if _talents != old_talents:
                        check = True
                        # Ситуация, когда появились надписи о героях, но не у всех игроков
                        for player in pre_game.players:
                            if not hasattr(player, 'hero'):
                                check = False
                                break

                        if check:
                            httshots.visual.tracker.create_image(pre_game.players)
                            httshots.visual.tracker.send_talents(pre_game.players)
                        old_talents = copy.deepcopy(_talents)

            except Exception as e:
                raise e

        await asyncio.sleep(5)


async def talents(ctx: commands.Context, hero=None):
    if not httshots.config.tracker_commands or not httshots.config.tracker_status:
        return

    if hero is None:
        return

    if httshots.check_talents_task is None:
        text = httshots.strings['TrackerNoActiveGame']
        await ctx.send(text)
        return

    hero = httshots.htts_data.get_hero_by_part(hero.strip())
    if hero is None:
        text = httshots.strings['TrackerNotFoundHero'].format(ctx.author.name)
        await ctx.send(text)
        return

    if os.path.isfile(httshots.config.tracker_events_file):
        file = open(httshots.config.tracker_events_file, 'rb')
        contents = file.read()
        file.close()

        if not httshots.stream_pregame:
            file = open(httshots.config.battle_lobby_file, 'rb')
            _contents = file.read()
            file.close()
            pre_game = httshots.parser.get_battle_lobby(_contents)
        else:
            pre_game = httshots.stream_pregame[-1]

        heroes = httshots.parser.ingame.parse_content(contents, pre_game)

        data_hero = httshots.htts_data.get_data_name(hero)

        if data_hero in heroes:
            _talents = heroes[data_hero]

            hero_name = httshots.htts_data.get_translate_hero(hero, 1)
            hots_hero_name = httshots.htts_data.remove_symbols(hero)
            talents = ''.join(map(str, _talents))
            tmp = f" [T{talents},{hots_hero_name}]"
            icy_hero = httshots.htts_data.get_icy_hero(hero).lower()
            icy_url = httshots.ICY_URL.format(icy_hero, talents.replace('0', '-'))
            text = httshots.strings['GameHeroTalents'].format(hero_name, tmp, icy_url)

            await ctx.send(text)
            return

        text = httshots.strings['TrackerNoHeroTalents'].format(ctx.author.name)
        await ctx.send(text)
        return

    text = httshots.strings['TrackerNoActiveGame']
    await ctx.send(text)
    return
