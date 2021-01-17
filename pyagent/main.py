from connection import Connection
import log
import packets

def test():
    conn = Connection()
    conn.send_packet(
        packets.PACKET_SERVER_JOIN_REQ,
        username = 'pyagent',
        capability = '+Freeciv-2.5-network fake',  # TODO, what capability do we need?
        #  NETWORK_CAPSTRING_MANDATORY="+Freeciv-2.5-network"
        #  NETWORK_CAPSTRING_OPTIONAL="nationset_change tech_cost split_reports extended_move_rate illness_ranges nonnatdef cheaper_small_wonders"
        version_label = '2.5.12',
        major_version = 2,
        minor_version = 5,
        patch_version = 12)

    while True:
        p = conn.get_packet()
        if p is not None:
            p.dump()
        else:
            import time
            time.sleep(1)

if __name__ == '__main__':
    test()
