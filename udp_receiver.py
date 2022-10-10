#!/usr/bin/env python3

import pickle
import signal
import socket
import sys

server = "127.0.0.1"
port = 20777
packets = []


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((server, port))

    try:
        receive(sock)
    except Exception:
        shutdown(None, None)


def shutdown(signal, frame):
    print("Writing data...")
    print("Shutting down...")


def receive(sock):
    # with open('telemetry.bin', 'wb') as f:
    while True:
        data, address = sock.recvfrom(2048)
        packets.append(data)


if __name__ == "__main__":
    signal.signal(signal.SIGBREAK, shutdown)
    main()
