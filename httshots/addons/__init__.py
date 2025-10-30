# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
from os import path
from glob import glob

from importlib import import_module

# httshots
from httshots import httshots


# ======================================================================
# >> ALL DECLARATION
# ======================================================================
_modules = glob(path.join(path.dirname(__file__), '*.py'))
modules = []

for _module in _modules:
    pre = path.basename(_module)[:-3]

    if pre.startswith("__"):
        continue

    module = import_module("httshots.addons." + pre)
    modules.append(module)


def load_addons(cfg):
    """Загрузка аддонов"""

    for mod in modules:
        _name = mod.__name__.split('.')[-1]
        if not _name in cfg:
            continue
        if cfg[_name].isdigit() and int(cfg[_name]) == 1:
            httshots.print_log('LoadAddon', _name, level=3)
            getattr(mod, "load")()
