
import os, re, sys

def generate_py_packets(types, packets):
    src_dir = os.path.dirname(sys.argv[0])
    my_root = src_dir + "/../pyagent/"

    f = open(my_root + "packets.py", "w")
    f.write("from dataio import Type, Field, Packet\n")
    f.write("\n")

    generate_packets(f, types, packets)

def generate_packets(f, types, packets):
    for p in packets:
        f.write("%s = Packet(\n" % p.type)
        f.write("    id      = %d,\n"   % p.type_number)
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

    f.write("packets = {\n")
    for p in sorted(packets, key = lambda p: p.type_number):
        f.write("    %3d : %s,\n" % (p.type_number, p.type))
    f.write("    }\n")

def generate_field(f, field):
    indent = " " * 8
    f.write("%sField(name = '%s',\n" % (indent, field.name))

    float_factor = ''
    if field.struct_type == 'float':
        float_factor = ', float_factor = %d' % field.float_factor

    f.write("%s      type = Type('%s', '%s'%s),\n" %
            (indent, field.dataio_type, field.struct_type, float_factor))

    f.write("%s      dimentions = []),\n" % indent)

#        for attrib in dir(p):
#            if not attrib.startswith("__") and not attrib.endswith("__"):
#                v = getattr(p, attrib)
#                if not callable(v):
#                    f.write("    %s = (%s) %s\n" % (attrib, type(v).__name__, v))
#        f.write("\n")
