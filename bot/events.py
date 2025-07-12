# ======================================================================
# >> Imports
# ======================================================================

# Python
from collections import defaultdict


# ======================================================================
# >> HttsEvents
# ======================================================================
class HttsEvents:
    def __init__(self):
        self.events = defaultdict(list)

    def register(self, event_name, _callback):
        if not self.is_register(event_name, _callback):
            self.events[event_name].append(_callback)

    def unregister(self, event_name, _callback):
        if _callback in self.events[event_name]:
            self.events[event_name].remove(_callback)

    def is_register(self, event_name, _callback):
        return _callback in self.events[event_name]

    def get_callbacks(self, event_name):
        if event_name in self.events:
            return self.events[event_name]

        return []

htts_events = HttsEvents()


# ======================================================================
# >> Events
# ======================================================================
def match_end(stream_replay):
    events = htts_events.get_callbacks("match_end")
    for _callback in events:
        _callback(stream_replay)


def match_start():
    events = htts_events.get_callbacks("match_start")
    for _callback in events:
        _callback()


async def bot_ready(bot):
    events = htts_events.get_callbacks("bot_ready")
    for _callback in events:
        await _callback(bot)


async def bot_setup_hook(bot):
    events = htts_events.get_callbacks("setup_hook")
    for _callback in events:
        await _callback(bot)
