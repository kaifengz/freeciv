from connection import Connection
import packets

def test():
    conn = Connection()
    conn.send(packets.PACKET_SERVER_JOIN_REQ(
        username = 'pyagent',
        capability = '',  # TODO, what capability do we need?
        version_label = '2.5.12',
        major_version = 2,
        minor_version = 5,
        patch_version = 12))

    p = conn.receive()
    p.dump()

if __name__ == '__main__':
    test()
