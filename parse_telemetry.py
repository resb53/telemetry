#!/usr/bin/env python3

import datetime
import pickle
import struct
import sys

packetSize = {
    0: 1464,
    1: 632,
    2: 972,
    3: 40,
    4: 1257,
    5: 1102,
    6: 1347,
    7: 1058,
    8: 1015,
    9: 1191,
    10: 948,
    11: 1155
}

eventSize = {
    "SSTA": 0,
    "SEND": 0,
    "FTLP": 5,
    "RTMT": 1,
    "DRSE": 0,
    "DRSD": 0,
    "TMPT": 1,
    "CHQF": 0,
    "RCWN": 1,
    "PENA": 7,
    "SPTP": 12,
    "STLG": 1,
    "LGOT": 0,
    "DTSV": 1,
    "SGSV": 1,
    "FLBK": 8,
    "BUTN": 4
}


class Packet():
    def __init__(self, header, body):
        self.size = len(body) + 24
        self.format = header[0]
        self.game_version = f"{str(header[1])}.{str(header[2])}"
        self.version = header[3]
        self.type = header[4]
        self.session = header[5]
        self.timestamp = header[6]
        self.frame = header[7]
        self.p1car = header[8]
        self.p2car = header[9]
        self.body = body


def main():
    # Load telemetry
    with open("telemetry.pickle", "rb") as f:
        telem = pickle.load(f)

    # Strip FINISH packet
    telem.pop(-1)

    # Iterate through packets and parse depending on type
    for rawPacket in telem:
        packet = parsePacket(rawPacket)

        if packet.size != packetSize[packet.type]:
            print(f"Size error! Packet type {packet.type} has size {packet.size}", file=sys.stderr)

        if packet.type in processData:
            processData[packet.type](packet)


def parsePacket(raw):
    header = raw[0:24]
    body = raw[24:]

    header = struct.unpack("=H4BQfI2B", header)
    packet = Packet(header, body)

    return packet


def processEvent(packet):
    eventType = packet.body[0:4]
    eventType = struct.unpack("4s", eventType)[0].decode("utf-8")
    body = packet.body[4:]

    print(f"{packet.timestamp}: {eventType}: {body}")


processData = {
    3: processEvent
}

if __name__ == "__main__":
    main()
