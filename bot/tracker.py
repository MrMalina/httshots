# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
import twitchio

# httshots
import httshots
from httshots import httshots


# ======================================================================
# >> Functions
# ======================================================================
def add_command(bot):
    command = twitchio.ext.commands.Command('talent', talent, aliases=("талант", ))
    bot.add_command(command)


async def talent(context, name=None):
    # print(context, name)
    ...