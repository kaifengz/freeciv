import socket

import dataio
import packets

class Connection:
    def __init__(self, host = '127.0.0.1', port = 5557):
        self.conn = socket.socket()
        self.conn.connect((host, port))

    def receive(self):
#        bytes = self.conn.recv(1024)
#        self._dump_bytes(bytes)
        pass

    def send(self, packet):
        self.conn.send(packet.serialize())

    def _dump_bytes(self, bytes):
        pass

