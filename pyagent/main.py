import itertools

import connection
import eventloop
import log
import packets

def main():
    conn = connection.Connection()
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

    eventloop.loop(conn)

@eventloop.register_packet_handler(packets.PACKET_CONN_PING)
def handle_conn_ping(conn, packet):
    log.log_verbose("Got a ping, sending a pong and a chat message ...")

    conn.send_packet(packets.PACKET_CONN_PONG)

    conn.send_packet(
            packets.PACKET_CHAT_MSG_REQ,
            message = "Hello, just got your ping")

if __name__ == '__main__':
    main()
