import datetime

import config

NONE    = 0
ERROR   = 1
INFO    = 2
VERBOSE = 3

def log_verbose(msg, *args):
    _log(VERBOSE, msg, args)

def log_info(msg, *args):
    _log(INFO, msg, args)

def log_error(msg, *args):
    _log(ERROR, msg, args)

_log_file = None
def _log(level, msg, args):
    if level <= config.log_level:
        if args:
            msg = msg % args

        time_str = datetime.datetime.now().strftime("%H:%M:%S.%f")

        global _log_file
        if _log_file is None:
            _log_file = open(config.log_file, "w")
            print("%s Starting" % time_str, file=_log_file)

        print("%s %s" % (time_str, msg), file=_log_file, flush=True)
        print(msg)

def log_bytes(bytes, offset = 0, length = None, msg = None, error = False):
    if not (config.enable_network_logging or (error and ERROR <= config.log_level)):
        return

    lines = []
    if msg:
        lines.append(msg)

    end = offset + length if length is not None else len(bytes)
    for start in range(offset, end, 16):
        line = bytes[start : min(start + 16, end)]
        hex_part = " ".join("%02X" % b for b in line)
        lit_part = "".join((chr(b) if 32 <= b < 127 else '.') for b in line)
        lines.append("%6d  %-50s%s" % ((start - offset) // 16, hex_part, lit_part))

    log_verbose('\n'.join(lines))
