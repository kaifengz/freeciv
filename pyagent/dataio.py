
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
    def __init__(self, **kwargs):
        pass

