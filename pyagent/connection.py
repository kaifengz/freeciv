import socket
import zlib

import config
import dataio
import log
import packets

class Connection:
    def __init__(self):
        self._conn = None

    def listen_and_accept(self, host = '127.0.0.1', port = 5558):
        sock = socket.socket()
        sock.bind((host, port))
        sock.listen()

        self._conn = sock.accept()[0]
        self._init_connection()

    def connect(self, host = '127.0.0.1', port = 5557):
        self._conn = socket.socket()
        self._conn.connect((host, port))
        self._init_connection()

    def _init_connection(self):
        assert self._conn is not None
        self._conn.setblocking(False)
        self.fileno = self._conn.fileno

        self._received_bytes = b''
        self._read_offset = 0

    def _receive(self):
        try:
            bytes = self._conn.recv(4 * 1024 * 1024)
        except BlockingIOError as err:
            return len(self._received_bytes) - self._read_offset

        log.log_bytes(bytes, msg = "Received %d bytes" % len(bytes))

        if not bytes:
            return len(self._received_bytes) - self._read_offset

        if self._read_offset == len(self._received_bytes):
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
        assert jumbo_packet_size > 6

        jumbo_packet_end = self._read_offset + jumbo_packet_size
        assert jumbo_packet_end <= len(self._received_bytes)

        bytes = self._received_bytes[ self._read_offset + 6 : jumbo_packet_end ]
        decompressed_bytes = zlib.decompress(bytes)

        log.log_bytes(
                decompressed_bytes,
                msg = "Decompressed a jumbo packet, compressed size %d, decompressed size %s" %
                    (len(bytes), len(decompressed_bytes)))

        if len(self._received_bytes) == jumbo_packet_end:
            self._received_bytes = decompressed_bytes
        else:
            self._received_bytes = decompressed_bytes + self._received_bytes[ jumbo_packet_end : ]

        self._read_offset = 0

    def get_packet(self):
        receive_called = False
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

        log.log_bytes(
                self._received_bytes, offset = self._read_offset, length = packet_size,
                msg = "Unpacking a packet of size %d" % packet_size)
        packet, real_packet_size = dataio.get_packet(packets.PACKETS, self._received_bytes, self._read_offset)
        assert packet_size == real_packet_size
        self._read_offset += packet_size

        return packet

    def send_packet(self, packet, **kwargs):
        if isinstance(packet, dataio.PacketInstance):
            assert not kwargs
            bytes = packet.packet.pack_instance(packet)

        elif isinstance(packet, dataio.Packet):
            bytes = packet.pack(kwargs)

        elif isinstance(packet, dataio.RawPacket):
            bytes = packet.bytes

        else:
            assert False, "Unknown argument type: %s" % packet

        log.log_bytes(bytes, msg = "Sending %d bytes" % len(bytes))
        self._conn.send(bytes)
