#!/usr/bin/env python3

from modules import f1Packets
import gzip
import pickle
import struct


def main():
    # Load telemetry
    with gzip.open("full_lap.gz", "rb") as f:
        telem = pickle.load(f)

    # Strip FINISH packet
    telem.pop(-1)

    # Iterate through packets and parse depending on type
    for rawPacket in telem:
        (header, body) = parsePacket(rawPacket)

        if header.type in processData:
            packet = processData[header.type](header, body)
            print(packet)


def parsePacket(raw):
    header = raw[0:24]
    body = raw[24:]

    header = f1Packets.Header(struct.unpack("=H4BQfI2B", header))

    return (header, body)


processData = {
    3: f1Packets.EventPacket
}

if __name__ == "__main__":
    main()
