import socket
import zlib

import config
import dataio
import log
import packets

class Connection:
    def __init__(self, host = '127.0.0.1', port = 5557):
        self._conn = socket.socket()
        self._conn.connect((host, port))

        self._received_bytes = None
        self._read_offset = 0

    def _receive(self):
        # TODO: make it unblocking
        bytes = self._conn.recv(4 * 1024 * 1024)
        self._dump_bytes(bytes, "Received %d bytes" % len(bytes))

        if not bytes:
            return len(self._received_bytes) - self._read_offset

        if self._received_bytes is None or self._read_offset == len(self._received_bytes):
            self._received_bytes = bytes
            self._read_offset = 0
            return len(self._received_bytes)

        elif self._read_offset == 0:
            self._received_bytes = self._received_bytes + bytes
            return len(self._received_bytes)

        else:
            self._received_bytes = self._received_bytes[self._read_offset:] + bytes
            self._read_offset = 0
            return len(self._received_bytes)

    def _decompress_jumbo_packet(self, jumbo_packet_size):
        assert self._received_bytes is not None
        assert jumbo_packet_size > 6

        jumbo_packet_end = self._read_offset + jumbo_packet_size
        assert jumbo_packet_end <= len(self._received_bytes)

        bytes = self._received_bytes[ self._read_offset + 6 : jumbo_packet_end ]
        decompressed_bytes = zlib.decompress(bytes)

        self._dump_bytes(
                decompressed_bytes,
                "Decompressed a jumbo packet, compressed size %d, decompressed size %s" %
                    (len(bytes), len(decompressed_bytes)))

        if len(self._received_bytes) == jumbo_packet_end:
            self._received_bytes = decompressed_bytes
        else:
            self._received_bytes = decompressed_bytes + self._received_bytes[ jumbo_packet_end : ]

        self._read_offset = 0

    def get_packet(self):
        receive_called = False

        unparsed_size = 0
        if self._received_bytes is not None:
            unparsed_size = len(self._received_bytes) - self._read_offset

        if unparsed_size < 2:
            unparsed_size = self._receive()
            if unparsed_size < 2:
                return None
            receive_called = True

        packet_size = dataio.unpack_uint16(self._received_bytes, self._read_offset, self._read_offset + 2)[0]
        if packet_size == dataio.JUMBO_SIZE:
            if unparsed_size < 6:
                if receive_called:
                    return None
                unparsed_size = self._receive()
                if unparsed_size < 6:
                    return None
                receive_called = True

            jumbo_packet_size = dataio.unpack_uint32(
                    self._received_bytes, self._read_offset + 2, self._read_offset + 6)[0]
            if unparsed_size < jumbo_packet_size:
                if receive_called:
                    return None
                unparsed_size = self._receive()
                if unparsed_size < jumbo_packet_size:
                    return None
                receive_called = True

            self._decompress_jumbo_packet(jumbo_packet_size)
            return self.get_packet()

        if unparsed_size < packet_size:
            if receive_called:
                return None
            unparsed_size = self._receive()
            if unparsed_size < packet_size:
                return None
            receive_called = True

        packet, real_packet_size = dataio.get_packet(packets.PACKETS, self._received_bytes, self._read_offset)
        assert packet_size == real_packet_size
        self._read_offset += packet_size

        return packet

    def send_packet(self, packet, **kwargs):
        bytes = packet.pack(kwargs)
        self._dump_bytes(bytes, "Sending %d bytes" % len(bytes))
        self._conn.send(bytes)

    def _dump_bytes(self, bytes, msg = None):
        if not config.enable_network_logging:
            return

        lines = []
        if msg:
            lines.append(msg)

        for offset in range(0, len(bytes), 16):
            line = bytes[offset : offset+16]
            hex_part = " ".join("%02X" % b for b in line)
            lit_part = "".join((chr(b) if 32 <= b < 127 else '.') for b in line)
            lines.append("%6d  %-50s%s" % (offset // 16, hex_part, lit_part))

        log.log_verbose('\n'.join(lines))

