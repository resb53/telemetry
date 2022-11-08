#!/usr/bin/env python3

from modules import f1Packets
import gzip
import pickle
import struct

packets = []


def main():
    # Load telemetry
    with gzip.open("telemetry.gz", "rb") as f:
        telem = pickle.load(f)

    # Strip FINISH packet
    telem.pop(-1)

    # Iterate through packets and parse depending on type
    for rawPacket in telem:
        (header, body) = parsePacket(rawPacket)

        if header.type == 6:
            packet = processData[header.type](header, body)
            print([x.gear for x in packet.cars])
            packets.append(packet)


def parsePacket(raw):
    header = raw[0:24]
    body = raw[24:]

    header = f1Packets.Header(struct.unpack("=H4BQfI2B", header))

    return (header, body)


processData = {
    0: f1Packets.MotionPacket,
    1: f1Packets.SessionPacket,
    2: f1Packets.LapDataPacket,
    3: f1Packets.EventPacket,
    4: f1Packets.ParticipantPacket,
    5: f1Packets.SetupPacket,
    6: f1Packets.TelemetryPacket,
    7: f1Packets.StatusPacket,
    8: f1Packets.ClassificationPacket,
    9: f1Packets.LobbyPacket,
    10: f1Packets.DamagePacket,
    11: f1Packets.HistoryPacket
}

if __name__ == "__main__":
    main()
