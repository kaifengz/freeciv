
import re

def generate_py_packets(types, packets):
    f = open("packets.py", "w")
    f.write("from dataio import Type, Field, Packet\n")
    f.write("\n")

    generate_types(f, types)
    generate_packets(f, types, packets)

def generate_types(f, types):
    type_dict = dict((type_.alias, type_.dest) for type_ in types)

    alias_dict = {}
    for alias, dest in type_dict.items():
        if dest in type_dict:
            alias_dict[alias] = dest
    for alias in alias_dict.keys():
        del type_dict[alias]

    types = []
    ptn = re.compile("^(.*)\((.*)\)$")
    for alias, dest in type_dict.items():
        m = ptn.search(dest)
        assert m, dest
        dataio_type, struct_type = m.groups()
        types.append((alias, dataio_type, struct_type))

    types.sort()
    type_name_max_len = max(len(type_[0]) for type_ in types)
    dataio_type_max_len = max(len(type_[1]) for type_ in types)
    for type_name, dataio_type, struct_type in types:
        f.write("%-*s = Type(%-*s'%s')\n" % (
                type_name_max_len + 1,
                type_name,
                dataio_type_max_len + 4,
                "'%s'," % dataio_type,
                struct_type))
    f.write("\n")

    alias_max_len = max(len(alias) for alias in alias_dict.keys())
    for alias, dest in sorted(alias_dict.items()):
        f.write("%-*s = %s\n" % (alias_max_len + 1, alias, dest))
    f.write("\n")

def generate_packets(f, types, packets):
    print("%d packets" % len(packets))
    for p in packets:
        f.write("%s = Packet(\n" % p.type)
        f.write("    id      = %d,\n"   % p.type_number)
        f.write("    name    = '%s',\n" % p.name)
        f.write("    sc      = %s,\n"   % ('sc' in p.dirs))
        f.write("    cs      = %s,\n"   % ('cs' in p.dirs))
        f.write("    is_info = '%s',\n" % p.is_info)
        f.write("    delta   = %s,\n"   % bool(p.delta))
        f.write("    fields  = [\n")
        f.write("    ])\n")
        f.write("\n")

#        for attrib in dir(p):
#            if not attrib.startswith("__") and not attrib.endswith("__"):
#                v = getattr(p, attrib)
#                if not callable(v):
#                    f.write("    %s = (%s) %s\n" % (attrib, type(v).__name__, v))
#        f.write("\n")
