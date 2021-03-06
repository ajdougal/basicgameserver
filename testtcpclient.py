#!/usr/bin/env python

import socket


TCP_IP = '192.168.1.5'
TCP_PORT = 10001
BUFFER_SIZE = 1024
MESSAGE = "192.168.1.5;10010;pnum:p1"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send(MESSAGE)
data = s.recv(BUFFER_SIZE)
s.close()

print ("received data:{}".format(data))