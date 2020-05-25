#!/usr/bin/env python

import threading
import socket


players = dict()

class ListeningThread(object):
    def __init__(self, interval=0.1):
        self.interval = interval
        self.tcp_inbound_ip = "192.168.1.5"
        self.tcp_inbound_port = 10001
        self.tcp_buffer_size = 1024

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('', self.tcp_inbound_port))
        self.s.listen(1)

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = False
        thread.start()

    def run(self):
        while True:
            conn, addr = self.s.accept()
            print ("Connection address:{}".format(addr))
            while 1:
                data = conn.recv(self.tcp_buffer_size)
                data_string = data.decode("utf-8")
                if not data: break
                split_message = data_string.split(";")
                players[split_message[2]] = dict()
                players[split_message[2]]["address"] = split_message[0]
                players[split_message[2]]["port"] = split_message[1]
                print ("received data:{}".format(addr))
                conn.send(data)
            conn.close()

ListeningThread()