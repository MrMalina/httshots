# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
from getpass import getuser

from configobj import ConfigObj
from os import path, sep, listdir
import mpyq

# Others
import heroprotocol
from heroprotocol import versions


# ======================================================================
# >> GLOBAL VARIABLES
# ======================================================================
__version__ = "0.0"

current_user = getuser()
hots_accounts_folder = f"c:\\Users\\{current_user}\\OneDrive\\Documents\\Heroes of the Storm\\Accounts\\"
if not path.isdir(hots_accounts_folder):
    hots_accounts_folder = f"c:\\Users\\{current_user}\\Documents\\Heroes of the Storm\\Accounts\\"


hots_replays_folder = hots_accounts_folder + "2-Hero-1-\d*\\Replays\Multiplayer\\"


# ======================================================================
# >> Load
# ======================================================================
def load():
    accounts = get_accounts_list(hots_accounts_folder)
    for x in accounts:
        replay = x.replays_path + list(x.replays)[0]
        break

    archive = mpyq.MPQArchive(replay)

    contents = archive.header['user_data_header']['content']
    header = heroprotocol.versions.latest().decode_replay_header(contents)

    baseBuild = header['m_version']['m_baseBuild']
    try:
        protocol = heroprotocol.versions.build(baseBuild)
    except:
        print('Unsupported base build: %d' % baseBuild, file=sys.stderr)
        sys.exit(1)

    contents = archive.read_file('replay.details')
    details = protocol.decode_replay_details(contents)

    print(details['m_playerList'][0]['m_hero'])

    print(details['m_playerList'][0]['m_hero'].decode('utf-8'))


    # Print protocol details
    # if args.details:
        # contents = archive.read_file('replay.details')
        # details = protocol.decode_replay_details(contents)
        # logger.log(sys.stdout, details)

    # Print protocol init data
    # if args.initdata:
        # contents = archive.read_file('replay.initData')
        # initdata = protocol.decode_replay_initdata(contents)
        # logger.log(
            # sys.stdout,
            # initdata['m_syncLobbyState']['m_gameDescription']['m_cacheHandles'],
        # )
        # logger.log(sys.stdout, initdata)

    # Print game events and/or game events stats
    # if args.gameevents:
        # contents = archive.read_file('replay.game.events')
        # for event in protocol.decode_replay_game_events(contents):
            # logger.log(sys.stdout, event)

    # Print message events
    # if args.messageevents:
        # contents = archive.read_file('replay.message.events')
        # for event in protocol.decode_replay_message_events(contents):
            # logger.log(sys.stdout, event)

    # Print tracker events
    # if args.trackerevents:
        # if hasattr(protocol, 'decode_replay_tracker_events'):
            # contents = archive.read_file('replay.tracker.events')
            # for event in protocol.decode_replay_tracker_events(contents):
                # logger.log(sys.stdout, event)

    # Print attributes events
    # if args.attributeevents:
        # contents = archive.read_file('replay.attributes.events')
        # attributes = protocol.decode_replay_attributes_events(contents)
        # logger.log(sys.stdout, attributes)

    print(details)


# ======================================================================
# >> Get Functions
# ======================================================================
def get_accounts_list(path):
    accounts = []

    folders = listdir(hots_accounts_folder)

    for folder in folders:
        id = folder.split(sep)[-1]
        accounts.append(Account(id))

    return accounts


# ======================================================================
# >> Classes
# ======================================================================
class Account:
    def __init__(self, id):
        self.id = id
        self.replays = []
        self.path = hots_accounts_folder + str(id) + "\\"

        self.get_unique_folder()
        self.replays_path = self.path + self.unique_folder + "\\Replays\Multiplayer\\"

        self.get_replays()

    def get_unique_folder(self):
        tmp = listdir(self.path)
        for folder in tmp:
            folder = folder.split(sep)[-1]
            if folder.startswith('2'):
                break

        self.unique_folder = folder

    def get_replays(self):
        self.replays = set(listdir(self.replays_path))

    def check_new_replays(self):
        replays = set(listdir(self.replays_path))
        check = replays.symmetric_difference(self.replays)
        self.replays = replays
        return check


load()
