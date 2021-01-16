import struct

JUMBO_SIZE = 0xFFFF

class Type:
    def __init__(self, dataio_type, struct_type, float_factor=None):
        self.dataio_type = dataio_type
        self.struct_type = struct_type
        self.float_factor = float_factor

class Field:
    def __init__(self, name, type, dimentions):
        self.name = name
        self.type = type
        self.dimentions = dimentions

        try:
            self._validate = globals()['validate_' + self.type.dataio_type]
        except KeyError:
            pass  # TODO

        try:
            self._pack = globals()['pack_' + self.type.dataio_type]
        except KeyError:
            pass  # TODO

    def validate_arg(self, arg):
        if not self._validate(arg):
            raise BadPacket("Invalid argument for field %s, expected %s" %
                    (self.name, self.type.dataio_type))

    def pack_arg(self, arg):
        return self._pack(arg)

class Packet:
    def __init__(self, id, name, sc, cs, is_info, delta, fields):
        self.id      = id
        self.name    = name
        self.sc      = sc
        self.cs      = cs
        self.is_info = is_info
        self.delta   = delta
        self.fields  = fields

    def __call__(self, **kwargs):
        return PacketInstance(self, kwargs)

class PacketInstance:
    def __init__(self, packet, args):
        self.packet = packet
        self.fields = packet.fields
        self.args = self._parse_args(args)

    def _parse_args(self, args):
        if len(args) != len(self.fields):
            raise BadPacket("Argument count %d does not match field count %d" %
                    (len(args), len(self.fields)))

        arg_values = []
        for field in self.fields:
            if field.name not in args:
                raise BadPacket("Argument %s is not specified" % field.name)

            arg = args[field.name]
            field.validate_arg(arg)
            arg_values.append(arg)
        return arg_values

    def pack(self):
        assert len(self.args) == len(self.fields)

        fragments = [
                pack_uint16(0),  # packet size
                pack_uint8(self.packet.id),
                ]
        for arg, field in zip(self.args, self.fields):
            fragments.append(field.pack_arg(arg))

        fragments[0] = pack_uint16(sum(map(len, fragments)))
        return b''.join(fragments)

    def dump(self):
        pass

class BadPacket(Exception):
    pass

def validate_uint8(n):
    return isinstance(n, int) and 0 <= n <= 0xFF

def pack_uint8(n):
    assert validate_uint8(n)
    return struct.pack('!B', n)

def unpack_uint8(bytes, offset):
    assert offset >= 0 and len(bytes) >= offset + 1
    n = struct.unpack_from('!B', bytes, offset)[0]
    return n, 1

def validate_uint16(n):
    return isinstance(n, int) and 0 <= n <= 0xFFFF

def pack_uint16(n):
    assert validate_uint16(n)
    return struct.pack('!H', n)

def unpack_uint16(bytes, offset):
    assert offset >= 0 and len(bytes) >= offset + 2
    n = struct.unpack_from('!H', bytes, offset)[0]
    return n, 2

def validate_uint32(n):
    return isinstance(n, int) and 0 <= n <= 0xFFFFFFFF

def pack_uint32(n):
    assert validate_uint32(n)
    return struct.pack('!I', n)

def unpack_uint32(bytes, offset):
    assert offset >= 0 and len(bytes) >= offset + 4
    n = struct.unpack_from('!I', bytes, offset)[0]
    return n, 4

def validate_string(s):
    return isinstance(s, str)

def pack_string(s):
    assert validate_string(s)
    return bytes(s, 'ascii') + b'\0'

def get_packet(packets, bytes, offset):
    packet_size = unpack_uint16(bytes, offset)[0]
    packet_id = unpack_uint8(bytes, offset + 2)[0]

    # TODO, not implemented
    return packets[packet_id].name, packet_size
