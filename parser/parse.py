# ======================================================================
# >> Imports
# ======================================================================

# httshots
import httshots
from httshots import httshots


# ======================================================================
# >> Functions
# ======================================================================
def decode_string(string):
    if isinstance(string, bytes):
        return string.decode('UTF-8')
    return string


# ======================================================================
# >> Classes
# ======================================================================
class Parse:
    def parse_data(self, section, data, cls=object):
        cfg = httshots.data_replay[section]

        for name, attr in cfg.items():
            key, _type = attr
            if "->" in key:
                tmp = key.split('->')
                _data = data[tmp[0]]
                value = _data[tmp[1]]
            else:
                value = data[key]

            if _type != 'A':
                method = getattr(TYPE, _type)
                if name == 'amm_id' and value is None:
                    value = 0
                attribute = method(value)
            else:
                attribute = Args(name, value)

            cls.__setattr__(self, name, attribute)


class Args(Parse):
    def __init__(self, name, data):
        self.parse_data(name, data)


class TYPE:
    I = int
    S = lambda x: decode_string(x)
    L = list
    B = bool
    F = float
    N = lambda x: x
    A = Args
