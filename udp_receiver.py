#!usr/bin/env python3

import pickle
import socket
import threading

stopping = False
server = "127.0.0.1"
port = 20777
packets = []


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((server, port))

    x = threading.Thread(target=receive, args=(sock,))
    x.start()

    finish()


def receive(sock):
    # with open('telemetry.bin', 'wb') as f:
    print("Listening...")
    while True:
        data, address = sock.recvfrom(2048)
        packets.append(data)
        global stopping
        if stopping:
            break
    with open("telemetry.pickle", 'wb') as f:
        pickle.dump(packets, f)
    print("Telemetry saved.")


def finish():
    while True:
        print("Type 'exit' to finish")
        ui = str(input())
        if ui == "exit":
            global stopping
            stopping = True
            terminate = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            terminate.sendto(bytes("FINISH", "utf-8"), (server, port))
            break


if __name__ == "__main__":
    main()
