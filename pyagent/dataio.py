
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
        pass

    def serialize(self):
        pass

    def dump(self):
        pass

