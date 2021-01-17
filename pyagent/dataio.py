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

        try:
            self._unpack = globals()['unpack_' + self.type.dataio_type]
        except KeyError:
            pass  # TODO

    def validate_arg(self, arg):
        if not self._validate(arg):
            raise BadPacket("Invalid argument for field %s, expected %s" %
                    (self.name, self.type.dataio_type))

    def pack_arg(self, arg):
        return self._pack(arg)

    def unpack(self, bytes, offset, end):
        return self._unpack(bytes, offset, end)

class Packet:
    def __init__(self, id, name, sc, cs, is_info, delta, fields):
        self.id      = id
        self.name    = name
        self.sc      = sc
        self.cs      = cs
        self.is_info = is_info
        self.delta   = delta
        self.fields  = fields

    def pack(self, kwargs):
        args = self._parse_args(kwargs)
        assert len(args) == len(self.fields)

        fragments = [
                pack_uint16(0),  # packet size
                pack_uint8(self.id),
                ]
        for arg, field in zip(args, self.fields):
            fragments.append(field.pack_arg(arg))

        fragments[0] = pack_uint16(sum(map(len, fragments)))
        return b''.join(fragments)

    def _parse_args(self, kwargs):
        if len(kwargs) != len(self.fields):
            raise BadPacket("Argument count %d does not match field count %d" %
                    (len(kwargs), len(self.fields)))

        args = []
        for field in self.fields:
            if field.name not in kwargs:
                raise BadPacket("Argument %s is not specified" % field.name)

            arg = kwargs[field.name]
            field.validate_arg(arg)
            args.append(arg)
        return args

    def unpack(self, bytes, offset, end):
        return PacketInstance.from_bytes(self, bytes, offset, end)

class PacketInstance:
    @classmethod
    def from_bytes(cls, packet, bytes, offset, end):
        original_offset = offset

        instance = cls()
        instance._packet = packet

        for field in packet.fields:
            value, value_size = field.unpack(bytes, offset, end)
            setattr(instance, field.name, value)
            offset += value_size

        if offset != end:
            raise BadPacket("Bytes not parsed correctly, got %d bytes, parsed %d" %
                    (end - original_offset, offset - original_offset))
        return instance

    def __str__(self):
        return '<%s at 0x%016x>' % (self._packet.name, id(self))

class BadPacket(Exception):
    pass

def validate_uint8(n):
    return isinstance(n, int) and 0 <= n <= 0xFF

def pack_uint8(n):
    assert validate_uint8(n)
    return struct.pack('!B', n)

def unpack_uint8(bytes, offset = 0, end = 1):
    assert 0 <= offset <= end - 1 and len(bytes) >= end
    n = struct.unpack_from('!B', bytes, offset)[0]
    return n, 1

def validate_uint16(n):
    return isinstance(n, int) and 0 <= n <= 0xFFFF

def pack_uint16(n):
    assert validate_uint16(n)
    return struct.pack('!H', n)

def unpack_uint16(bytes, offset = 0, end = 2):
    assert 0 <= offset <= end - 2 and len(bytes) >= end
    n = struct.unpack_from('!H', bytes, offset)[0]
    return n, 2

def validate_uint32(n):
    return isinstance(n, int) and 0 <= n <= 0xFFFFFFFF

def pack_uint32(n):
    assert validate_uint32(n)
    return struct.pack('!I', n)

def unpack_uint32(bytes, offset = 0, end = 4):
    assert 0 <= offset <= end - 4 and len(bytes) >= end, (bytes, offset, end)
    n = struct.unpack_from('!I', bytes, offset)[0]
    return n, 4

def validate_string(s):
    return isinstance(s, str)

def pack_string(s):
    assert validate_string(s)
    return bytes(s, 'ascii') + b'\0'

def get_packet(packets, bytes, offset):
    packet_size = unpack_uint16(bytes, offset, offset + 2)[0]
    packet_id = unpack_uint8(bytes, offset + 2, offset + 3)[0]

    return packets[packet_id].unpack(bytes, offset + 3, packet_size), packet_size
