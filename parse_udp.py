#!/usr/bin/env python3

# https://answers.ea.com/t5/General-Discussion/F1-22-UDP-Specification/td-p/11551274

import struct

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

line = 1

with open("./telemetry.bin", "rb") as telem:
    while (telem.peek(1) != b""):
        header = telem.read(24)

        # [uint16,uint8,uint8,uint8,uint8,uint64,float32,uint32,uint8,uint8]
        hfields = struct.unpack("=H4BQfI2B", header)
        print(f"{line}: {hfields}")
        print(hfields[4])

        body = telem.read(packetSize[hfields[4]])

        if hfields[4] == 3:
            event = struct.unpack("=4s", body)
            event = event[0].decode("utf8")
            print(event)
            body = telem.read(eventSize[event])

        footer = telem.read(8)
        print(footer)

        if line == 5:
            break
        else:
            line += 1
