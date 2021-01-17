
import os, re, sys

def generate_py_packets(types, packets):
    src_dir = os.path.dirname(sys.argv[0])
    my_root = src_dir + "/../pyagent/"

    f = open(my_root + "packets.py", "w")
    f.write("from dataio import Type, Field, Packet\n")
    f.write("from constants import *\n")
    f.write("\n")

    generate_packets(f, types, packets)

def generate_packets(f, types, packets):
    for p in packets:
        f.write("%s = Packet(\n" % p.type)
        f.write("    id      = %d | 0x%02X,\n" % (p.type_number, p.type_number))
        f.write("    name    = '%s',\n" % p.name)
        f.write("    sc      = %s,\n"   % ('sc' in p.dirs))
        f.write("    cs      = %s,\n"   % ('cs' in p.dirs))
        f.write("    is_info = '%s',\n" % p.is_info)
        f.write("    delta   = %s,\n"   % bool(p.delta))
        f.write("    fields  = [\n")

        for field in p.fields:
            generate_field(f, field)

        f.write("    ])\n")
        f.write("\n")

    f.write("PACKETS = {\n")
    for p in sorted(packets, key = lambda p: p.type_number):
        f.write("    %3d | 0x%02X : %s,\n" % (p.type_number, p.type_number, p.type))
    f.write("    }\n")

def generate_field(f, field):
    indent = " " * 8
    f.write("%sField(name = '%s',\n" % (indent, field.name))

    float_factor = ''
    if field.struct_type == 'float':
        float_factor = ', float_factor = %d' % field.float_factor

    f.write("%s      type = Type('%s', '%s'%s),\n" %
            (indent, field.dataio_type, field.struct_type, float_factor))

    if field.dataio_type == 'string':
        assert 1 <= field.is_array <= 2
        dimention = None if field.is_array == 1 else field.array_size1_u
    else:
        assert 0 <= field.is_array <= 1
        dimention = None if field.is_array == 0 else field.array_size_u

    if dimention is not None:
        arrow = dimention.find('->')
        if arrow >= 0:
            dimention = "'%s'" % dimention[ arrow+2 : ]

    f.write("%s      dimention = %s),\n" % (indent, dimention))

#        for attrib in dir(p):
#            if not attrib.startswith("__") and not attrib.endswith("__"):
#                v = getattr(p, attrib)
#                if not callable(v):
#                    f.write("    %s = (%s) %s\n" % (attrib, type(v).__name__, v))
#        f.write("\n")
