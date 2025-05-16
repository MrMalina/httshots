from heroprotocol.decoders import BitPackedBuffer

class BLPlayer:
    def __init__(self, index):
        self.userid = index
        self.talents = [0, 0, 0, 0, 0, 0, 0]

    def __repr__(self):
        return f"{self.battle_tag} ({self.tag}) - party {self.party} - level {self.level}"


def get_battle_lobby_players(contents):
    blplayers = []

    buffer = BitPackedBuffer(contents, 'big')
    s2m_array_length = buffer.read_bits(8)
    string_length = buffer.read_bits(8)

    buffer.read_aligned_bytes(string_length)

    for _ in range(s2m_array_length-1):
        buffer.read_bits(16)
        buffer.read_aligned_bytes(string_length)

    # s2m error
    if buffer.read_bits(8) != s2m_array_length:
        return None

    for _ in range(s2m_array_length):
        buffer.read_aligned_bytes(4)
        buffer.read_bits(2*8)
        buffer.read_aligned_bytes(2)
        buffer.read_bits(32*8)

    buffer.read_aligned_bytes(1)

    while True:
        x = buffer.read_aligned_bytes(4)
        if x == b"s2mh":
            buffer._used -= 4
            break
        buffer._used -= 3

    for _ in range(s2m_array_length):
        buffer.byte_align()
        a = buffer.read_aligned_bytes(4)
        # s2mh error
        if a != b"s2mh":
            return None
        buffer.read_bits(2*8)
        buffer.read_aligned_bytes(2)
        buffer.read_bits(32*8)

    collection_size = buffer.read_bits(16)

    for x in range(collection_size):
        buffer.read_aligned_bytes(8)

    a = buffer.read_bits(32)
    # collection_size error
    if a != collection_size:
        return None

    for _ in range(collection_size):
        for _ in range(16):
            buffer.read_bits(8)
            buffer.read_bits(8)

    disabled_hero_list_length = buffer.read_bits(8)

    for x in range(disabled_hero_list_length):
        buffer.read_aligned_bytes(32)

    # randomValue
    buffer.read_bits(32)

    buffer.read_bits(32)

    player_list_length = buffer.read_bits(5)

    for x in range(player_list_length):
        buffer.read_bits(32)

        index = buffer.read_bits(5)

        blplayer = BLPlayer(index)

        #toon
        buffer.read_bits(8) # region
        program_id = buffer.read_bits(32)
        program_id = program_id.to_bytes((program_id.bit_length() + 7) // 8, byteorder='big')

        # unknown game
        if program_id != b'Hero':
            return None

        buffer.read_bits(32) # realm
        buffer.read_bits(64) # id

        buffer.read_bits(8) # region
        program_id = buffer.read_bits(32)
        program_id = program_id.to_bytes((program_id.bit_length() + 7) // 8, byteorder='big')

        # unknown game
        if program_id != b'Hero':
            return None

        buffer.read_bits(32) # realm

        _id = buffer.read_bits(7) + 2
        buffer.byte_align()
        tag = buffer.read_aligned_bytes(_id)
        blplayer.tag = tag

        buffer.read_bits(6)

        buffer.read_bits(2)
        buffer.read_bits(25*8)
        buffer.read_bits(24)

        buffer.read_bits(7)

        bit = buffer.read_bits(1)
        if not bit:
            buffer.read_bits(12)
            buffer.read_bits(1)

        blplayer.has_silence_penalty = buffer.read_bits(1)
        buffer.read_bits(1)
        blplayer.has_voice_silence_penalty = buffer.read_bits(1)
        blplayer.is_blizzard_staff = buffer.read_bits(1)

        # player party id
        if buffer.read_bits(1):
            blplayer.party = buffer.read_bits(32) + buffer.read_bits(32)
        else:
            blplayer.party = 0

        buffer.read_bits(1)
        lenght = buffer.read_bits(7)
        buffer.byte_align()
        battle_tag = buffer.read_aligned_bytes(lenght)
        blplayer.battle_tag = battle_tag.decode('UTF8')

        # battle_tag lenght error
        if len(battle_tag) == 2:
            return None

        level = buffer.read_bits(32)
        blplayer.level = level
        blplayer.has_active_boost = buffer.read_bits(1)

        blplayers.append(blplayer)

    return blplayers
