# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
from twitchio.ext import commands
import os

# httshots
import httshots
from httshots import httshots


# ======================================================================
# >> Functions
# ======================================================================
def add_command(bot):
    command = commands.Command('talent', talent, aliases=("талант", ))
    bot.add_command(command)


def try_find_hero(hero_name_part):
    print(hero_name_part)
    for hero in httshots.data_heroes['names']:
        if hero.lower().startswith(hero_name_part):
            print(1, hero)
            return hero

    for _hero in httshots.data_heroes['rofl_names']:
        if _hero.lower().startswith(hero_name_part):
            hero_name_part = httshots.data_heroes['rofl_names'][_hero].lower()
            break

    for hero in httshots.data_heroes['names']:
        if hero.lower().startswith(hero_name_part):
            return hero

    return None


def rus_to_eng_hero_name(hero_name):
    hero = httshots.data_heroes['en'][hero_name]
    return httshots.data_heroes['herodata'].get(hero, hero)


@commands.cooldown(rate=1, per=5, bucket=commands.Bucket.channel)
async def talent(ctx: commands.Context, hero=None):
    # if len(httshots.stream_replays) == len(httshots.stream_pregame):
        # text = httshots.strings['TrackerNoActiveGame']
        # await ctx.send(text)
        # return

    if hero is None:
        return

    hero = try_find_hero(hero.lower().strip())
    if hero is None:
        text = httshots.strings['GameNotFoundHero'].format(ctx.author.name)
        await ctx.send(text)
        return

    if os.path.isfile(httshots.tracker_events_file):
        file = open(httshots.tracker_events_file, 'rb')
        contents = file.read()
        file.close()

        if not len(httshots.stream_pregame):
            file = open(httshots.battle_lobby_file, 'rb')
            _contents = file.read()
            file.close()
            pre_game = httshots.parser.get_battle_lobby(_contents)
        else:
            pre_game = httshots.stream_pregame[-1]

        heroes = httshots.parser.ingame.parse_content(contents, pre_game)
        hero_eng = rus_to_eng_hero_name(hero)

        if hero_eng in heroes:
            print(heroes[hero_eng])

            talents = heroes[hero_eng]

            hero_name = httshots.data_heroes['names'].get(hero, [0,0,0,0,0])[0]
            hero_name_eng = httshots.data_heroes['en'].get(hero, None)

            # print(

            talents = ''.join(map(str, talents))
            tmp = f" [T{talents},{hero_name_eng}]"
            icy_hero = httshots.data_heroes['icy'].get(hero, hero_name_eng.lower())
            icy_url = httshots.icy_url.format(icy_hero, talents.replace('0', '-'))
            text = httshots.strings['GameHeroTalents'].format(hero_name, tmp, icy_url)
            await ctx.send(text)
            return

        else:
            text = httshots.strings['GameNotFoundHero'].format(ctx.author.name)
            await ctx.send(text)
            return

    else:
        text = httshots.strings['TrackerNoActiveGame']
        await ctx.send(text)
        return