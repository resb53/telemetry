#!/usr/bin/env python3

import socket

server = "127.0.0.1"
port = 20777

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((server, port))

with open('telemetry.bin', 'wb') as f:
    while True:
        data, address = sock.recvfrom(4096)
        f.write(data)
