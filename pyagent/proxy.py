import itertools
import queue
import select
import time

import connection
import eventloop
import log
import packets

class Proxy:
    def __init__(self):
        self._client_conn = connection.Connection()
        self._server_conn = connection.Connection()

        self._client_packets = queue.Queue()
        self._server_packets = queue.Queue()

    def establish_connections(self):
        self._client_conn.listen_and_accept()
        self._server_conn.connect(port = 5556)

        self._conn_list = [
                self._client_conn.fileno(),
                self._server_conn.fileno(),
                ]

    def mainloop(self):
        while True:
            ready_fileno_list = select.select(
                    self._conn_list, [], [])[0]

            for fileno in ready_fileno_list:
                if fileno == self._client_conn.fileno():
                    self._on_read_client()
                elif fileno == self._server_conn.fileno():
                    self._on_read_server()

    def _on_read_client(self):
        while True:
            p = self._client_conn.get_packet()
            if p is None:
                break

            p.dump("Received from client: ")
            self._server_conn.send_packet(p)

    def _on_read_server(self):
        while True:
            p = self._server_conn.get_packet()
            if p is None:
                break

            p.dump("Received from server: ")
            self._client_conn.send_packet(p)

def main():
    proxy = Proxy()
    proxy.establish_connections()
    proxy.mainloop()

if __name__ == '__main__':
    main()

