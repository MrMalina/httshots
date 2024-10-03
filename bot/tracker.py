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


@commands.cooldown(rate=1, per=5, bucket=commands.Bucket.channel)
async def talent(ctx: commands.Context, hero=None):
    # if len(httshots.stream_replays) == len(httshots.stream_pregame):
        # text = httshots.strings['TrackerNoActiveGame']
        # await ctx.send(text)
        # return

    if hero is None:
        return

    hero = httshots.hero_names.get_hero_by_part(hero.lower().strip())
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

        hero_eng = httshots.hero_names.get_eng_hero(hero)

        if hero_eng in heroes:
            talents = heroes[hero_eng]

            hero_name = httshots.hero_names.get_hero(hero, 0)
            hero_name_eng = httshots.hero_names.get_eng_hero(hero)
            talents = ''.join(map(str, talents))
            tmp = f" [T{talents},{hero_name_eng}]"
            icy_hero = httshots.hero_names.get_icy_hero(hero, hero_name_eng.lower())
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