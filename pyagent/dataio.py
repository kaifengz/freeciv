import struct

import log

JUMBO_SIZE = 0xFFFF

class Type:
    def __init__(self, dataio_type, struct_type, float_factor=None):
        self.dataio_type = dataio_type
        self.struct_type = struct_type
        self.float_factor = float_factor

class Field:
    def __init__(self, name, type, dimention):
        self.name = name
        self.type = type
        self.dimention = dimention

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
        try:
            return self._unpack(bytes, offset, end)
        except AttributeError:
            log.log_error("unpack_%s is not defined!", self.type.dataio_type)
            raise

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

        if self.delta:
            fragments.append(pack_bitvector([arg is not None for arg in args]))

        for arg, field in zip(args, self.fields):
            if arg is not None:
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
            if arg is None:
                if not self.delta:
                    raise BadPacket("Argument %s should not be None as %s is no-delta" %
                            (field.name, self.name))
            else:
                field.validate_arg(arg)
            args.append(arg)
        return args

    def unpack(self, bytes, offset, end):
        try:
            return PacketInstance.from_bytes(self, bytes, offset, end)
        except UnpackError:
            log.log_bytes(bytes, offset - 3, length = end - offset + 3, error = True,
                    msg = "Unable to unpack %s of size %d" % (self.name, end - offset + 3))
            pass  # raise
        except:
            pass

        # TODO
        log.log_error("Unpack error for %s is temporarily suppressed", self.name)
        return None

class PacketInstance:
    @classmethod
    def from_bytes(cls, packet, bytes, offset, end):
        original_offset = offset

        instance = cls()
        instance.packet = packet

        if packet.delta:
            have_field, bitvector_size = unpack_bitvector(bytes, offset, end, len(packet.fields))
            assert len(have_field) == len(packet.fields)
            offset += bitvector_size

        for idx, field in enumerate(packet.fields):
            if packet.delta and not have_field[idx]:
                setattr(instance, field.name, None)
                continue

            dimention = field.dimention
            if dimention is None:
                value, value_size = field.unpack(bytes, offset, end)
                setattr(instance, field.name, value)
                offset += value_size

            else:
                if not isinstance(dimention, int):
                    assert isinstance(dimention, str)
                    dimention = getattr(self, dimention)
                    assert isinstance(dimention, int)

                values = []
                for i in range(dimention):
                    value, value_size = field.unpack(bytes, offset, end)
                    values.append(value)
                    offset += value_size
                setattr(instance, field.name, values)

        if offset != end:
            raise BadPacket("Bytes not parsed correctly, got %d bytes, parsed %d" %
                    (end - original_offset, offset - original_offset))
        return instance

    def __str__(self):
        return '<%s at 0x%016x>' % (self.packet.name, id(self))

    def dump(self):
        lines = [
                "%s at 0x%016x" % (self.packet.name, id(self))
                ]

        for field in self.packet.fields:
            lines.append("%20s = %s" % (field.name, getattr(self, field.name)))
        log.log_verbose('\n'.join(lines))

class BadPacket(Exception):
    pass

class UnpackError(Exception):
    pass

def unpack_bool8(bytes, offset, end):
    assert 0 <= offset <= end - 1 and len(bytes) >= end
    n = struct.unpack_from('!B', bytes, offset)[0]
    return bool(n), 1

def validate_uint8(n):
    return isinstance(n, int) and 0 <= n <= 0xFF

def pack_uint8(n):
    assert validate_uint8(n)
    return struct.pack('!B', n)

def unpack_uint8(bytes, offset, end):
    if not (0 <= offset <= end - 1 and len(bytes) >= end):
        raise UnpackError("Insuffient bytes for uint8, need 1, got %d" %
                (end - offset))

    n = struct.unpack_from('!B', bytes, offset)[0]
    return n, 1

def validate_uint16(n):
    return isinstance(n, int) and 0 <= n <= 0xFFFF

def pack_uint16(n):
    assert validate_uint16(n)
    return struct.pack('!H', n)

def unpack_uint16(bytes, offset, end):
    if not (0 <= offset <= end - 2 and len(bytes) >= end):
        raise UnpackError("Insuffient bytes for uint16, need 2, got %d" %
                (end - offset))

    n = struct.unpack_from('!H', bytes, offset)[0]
    return n, 2

def unpack_sint16(bytes, offset, end):
    if not (0 <= offset <= end - 2 and len(bytes) >= end):
        raise UnpackError("Insuffient bytes for sint16, need 2, got %d" %
                (end - offset))

    n = struct.unpack_from('!h', bytes, offset)[0]
    return n, 2

def validate_uint32(n):
    return isinstance(n, int) and 0 <= n <= 0xFFFFFFFF

def pack_uint32(n):
    assert validate_uint32(n)
    return struct.pack('!I', n)

def unpack_uint32(bytes, offset, end):
    if not (0 <= offset <= end - 4 and len(bytes) >= end):
        raise UnpackError("Insuffient bytes for uint32, need 4, got %d" %
                (end - offset))

    n = struct.unpack_from('!I', bytes, offset)[0]
    return n, 4

def unpack_sint32(bytes, offset, end):
    if not (0 <= offset <= end - 4 and len(bytes) >= end):
        raise UnpackError("Insuffient bytes for sint32, need 4, got %d" %
                (end - offset))

    n = struct.unpack_from('!i', bytes, offset)[0]
    return n, 4

def validate_string(s):
    return isinstance(s, str)

def pack_string(s):
    assert validate_string(s)
    return bytes(s, 'ascii') + b'\0'

def unpack_string(bytes, offset, end):
    if not (0 <= offset < end <= len(bytes)):
        raise UnpackError("Insuffient bytes for string, need at least 1, got %d" %
                (end - offset))

    null_byte = bytes.find(b'\0', offset, end)
    if null_byte < 0:
        raise UnpackError("Isn't the string null-terminated? bytes = %s, length = %d" %
                (bytes[offset : end], end - offset))

    return bytes[offset : null_byte].decode('utf8'), null_byte - offset + 1

def pack_bitvector(bitvector):
    n = 0
    for boolean in bitvector:
        n = n * 2 + int(boolean)

    bitvector_size = (len(bitvector) + 7) // 8
    bytes_ = [None] * bitvector_size
    for idx in range(bitvector_size):
        bytes_[idx] = n % 0x100
        n //= 0x100
    return bytes(bytes_)

def unpack_bitvector(bytes, offset, end, bitvector_length):
    bitvector_size = (bitvector_length + 7) // 8
    if not (0 <= offset and 0 < bitvector_size and offset + bitvector_size <= end <= len(bytes)):
        raise UnpackError("Insuffient bytes for bitvector, offset %d, end %d, bitvector_length %d, len(bytes) %d" %
                (offset, end, bitvector_length, len(bytes)))

    bits = struct.unpack_from('%dB' % bitvector_size, bytes, offset)
    n = 0
    for b in reversed(bits):
        n = (n << 8) + b

    bitvector = []
    for idx in range(bitvector_length):
        bitvector.append(n % 2 != 0)
        n //= 2
    return bitvector, bitvector_size

def get_packet(packets, bytes, offset):
    packet_size = unpack_uint16(bytes, offset, offset + 2)[0]
    packet_id = unpack_uint8(bytes, offset + 2, offset + 3)[0]

    return packets[packet_id].unpack(bytes, offset + 3, offset + packet_size), packet_size
