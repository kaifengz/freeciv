import socket

import dataio
import config
import packets

class Connection:
    def __init__(self, host = '127.0.0.1', port = 5557):
        self._conn = socket.socket()
        self._conn.connect((host, port))

    def receive(self):
        bytes = self._conn.recv(1024)
        self._dump_bytes(bytes, "Received %d bytes" % len(bytes))
        pass  # TODO

    def send(self, packet):
        bytes = packet.pack()
        self._dump_bytes(bytes, "Sending %d bytes" % len(bytes))
        self._conn.send(packet.pack())

    def _dump_bytes(self, bytes, msg = None):
        if not config.enable_network_logging:
            return

        if msg:
            print(msg)

        for idx, b in enumerate(bytes):
            print("%02X" % b, end = ('\n' if (idx % 16 == 15) else ' '))
        if len(bytes) % 16 != 0:
            print()

