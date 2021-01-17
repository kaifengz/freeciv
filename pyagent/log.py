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
    if level<= config.log_level:
        if args:
            msg = msg % args

        time_str = datetime.datetime.now().strftime("%H:%M:%S.%f")

        global _log_file
        if _log_file is None:
            _log_file = open(config.log_file, "w")
            print("%s Starting" % time_str, file=_log_file)

        print("%s %s" % (time_str, msg), file=_log_file, flush=True)
        print(msg)
