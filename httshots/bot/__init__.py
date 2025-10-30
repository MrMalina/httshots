# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
import asyncio
import asqlite

# twitchio
import twitchio
from twitchio.ext import commands
from twitchio import eventsub
from twitchio.exceptions import HTTPException

# httshots
import httshots as hots
from httshots import httshots
from . import bot
from . import replays
from . import score
from . import pregame
from . import events


# ======================================================================
# >> TwitchBot
# ======================================================================
class TwitchBot(commands.Bot):
    def __init__(self, client_id: str, client_secret: str,
                 bot_id: str, owner_id: str, prefix: str,
                 token_database: asqlite.Pool):
        self.token_database = token_database
        super().__init__(
                    client_id=client_id,
                    client_secret=client_secret,
                    bot_id=bot_id,
                    owner_id=owner_id,
                    prefix=prefix
                )

    async def setup_hook(self) -> None:
        await self.add_component(bot.BotCommands(self))
        chat_message = eventsub.ChatMessageSubscription(broadcaster_user_id=str(self.owner_id),
                                                        user_id=str(self.bot_id))
        try:
            await self.subscribe_websocket(payload=chat_message, as_bot=True)
        except HTTPException as e:
            if e.extra['message'] == 'invalid transport and auth combination':
                httshots.print_log('BotTransportError', level=5)
                httshots.print_log('BotStop', level=5)
                httshots.STOPPED = 1

        await events.bot_setup_hook(self)


    async def add_token(self, token: str, refresh: str) -> twitchio.authentication.ValidateTokenPayload:
        # Make sure to call super() as it will add the tokens interally and return us some data...
        resp: twitchio.authentication.ValidateTokenPayload = await super().add_token(token, refresh)

        # Store our tokens in a simple SQLite Database when they are authorized...
        query = """
        INSERT INTO tokens (user_id, token, refresh)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET
            token = excluded.token,
            refresh = excluded.refresh;
        """

        async with self.token_database.acquire() as connection:
            await connection.execute(query, (resp.user_id, token, refresh))

        if httshots.config.debug:
            httshots.print_log("BotAddToken", resp.user_id, level=5)
        return resp

    async def load_tokens(self, path: str | None = None) -> None:
        # We don't need to call this manually, it is called in .login() from .start() internally...

        async with self.token_database.acquire() as connection:
            rows: list = await connection.fetchall("""SELECT * from tokens""")

        for row in rows:
            if httshots.config.debug:
                print(row["token"], row["refresh"])
            await self.add_token(row["token"], row["refresh"])

    async def setup_database(self) -> None:
        # Create our token table, if it doesn't exist..
        query = """CREATE TABLE IF NOT EXISTS tokens(user_id TEXT PRIMARY KEY, token TEXT NOT NULL, refresh TEXT NOT NULL)"""
        async with self.token_database.acquire() as connection:
            await connection.execute(query)

    async def _send_message(self, message: str) -> None:
        await self.chat.send_message(sender=self.user, message=message)

    async def event_ready(self) -> None:
        self.chat = self.create_partialuser(user_id=str(self.owner_id))

        channel = await self.fetch_channel(self.owner_id)
        httshots.print_log('ReadyInfo', self.user, self.bot_id,
                            channel.user, level=4)

        if httshots.config.add_previous_games == 1:
            consider_matches = httshots.config.matches_type_to_consider
            starting_hour = httshots.config.starting_hour
            found = 0
            replayes_count = 0
            acc_names = httshots.config.accounts
            for acc in httshots.accounts:
                acc_replays = list(acc.get_all_replays())
                for replay_path in acc_replays:
                    replayes_count += 1
                    tmp = httshots.parser.get_replay(replay_path)
                    # На случай попытки прочитать реплей старой версии
                    if tmp is None:
                        continue

                    replay, protocol = tmp
                    info = httshots.parser.get_match_info(replay, protocol)
                    replay_title = replay_path.split('/')[-1]

                    if httshots.config.debug:
                        print(replay_path, replay_title)

                    if info == -1:
                        httshots.print_log('FoundPreviousGameSkipPlayers',
                                            replay_title[11:-12], level=1)
                        continue

                    tmp = replay_title.split()
                    hour = int(tmp[1][:2])
                    if starting_hour > hour:
                        httshots.print_log('FoundPreviousGameSkipTime',
                                            replay_title[11:-12], starting_hour,
                                            level=1)
                        continue

                    me = None
                    players = {x.name:x for x in info.players.values()}
                    for acc_name in acc_names:
                        if acc_name in players:
                            me = players[acc_name]
                            break

                    amm_id = info.game_type
                    if consider_matches == 2 or amm_id == 50091:
                        if me is None:
                            httshots.print_log('FoundPreviousGameNoAcc',
                                                replay_title[11:-12],
                                                level=1)
                            continue

                        if me.result == 1:
                            if httshots.streak[0] == 'Wins':
                                httshots.streak[1] += 1
                            else:
                                httshots.streak[0] = 'Wins'
                                httshots.streak[1] = 1
                        else:
                            if httshots.streak[0] == 'Loses':
                                httshots.streak[1] += 1
                            else:
                                httshots.streak[0] = 'Loses'
                                httshots.streak[1] = 1

                        found = 1

                        sreplay = httshots.StreamReplay(replay_title, me, info)
                        httshots.stream_replays.append(sreplay)
                        sreplay.url_games = None
                        httshots.print_log('FoundRankedPreviousGame',
                                            me.name, replay_title[11:-12],
                                            level=1)
                    else:
                        httshots.print_log('FoundNoRankedPreviousGames',
                                            me.name, replay_title[11:-12],
                                            level=1)

            if found:
                # 2024-11-28 21.35.03 Завод Вольской -> 24-11-28 21-35
                tmp = replay_title.split()
                httshots.cur_game[0] = tmp[0][2:]
                httshots.cur_game[1] = tmp[1][:-3].replace('.', '-')

                if httshots.config.image_upload:
                    # Единожды сортируем, так как чтение реплеев не обязательно по возрастающему времени
                    _replays = sorted(httshots.stream_replays, key=lambda x: x.title)
                    httshots.stream_replays = list(_replays)
                    url_games = httshots.visual.games.create_image()
                    httshots.stream_replays[-1].url_games = url_games

                httshots.print_log('FoundPreviousGames', replayes_count,
                                    len(httshots.stream_replays), level=2)

            elif consider_matches == 1:
                httshots.print_log('FoundZeroLeaguePreviousGames', level=2)
            else:
                httshots.print_log('FoundZeroPreviousGames', level=2)

        if httshots.config.score_use:
            httshots.bot.score.update_score()

        httshots.print_log('BotStarted', hots.pkg_name,
                           hots.pkg_author, hots.pkg_version,
                           level=4)

        await events.bot_ready(self)

        await self.endless_loop()

    async def endless_loop(self):
        if httshots.config.battlelobby_status == 1:
            while True:
                await replays.check_replays()
                await pregame.check_battle_lobby()
                await asyncio.sleep(httshots.config.replay_check_period)
        else:
            while True:
                await replays.check_replays()
                await asyncio.sleep(httshots.config.replay_check_period)
