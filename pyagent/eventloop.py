import itertools
import time

_packet_handlers = {}
_idle_handler = None

def loop(conn):
    for count in itertools.count(1):
        p = conn.get_packet()
        if p is not None:
            handler = _packet_handlers.get(p.packet.id)
            if handler is None:
                p.dump()
            else:
                handler(conn, p)

        # TODO: not really "idle" now
        if count % 100 == 0:
            if _idle_handler is not None:
                _idle_handler(conn)
            time.sleep(0.1)

class register_packet_handler:
    def __init__(self, packet):
        self._packet = packet

    def __call__(self, handler):
        assert self._packet.id not in _packet_handlers, \
                "packet handler for %s is already registered: %s" % (
                        self._packet.name, _packet_handlers[self._packet.id])

        _packet_handlers[self._packet.id] = handler

def register_idle_handler(handler):
    global _idle_handler

    assert _idle_handler is None, "idle handler is already registered: %s" % (
            _idle_handler)

    _idle_handler = handler
