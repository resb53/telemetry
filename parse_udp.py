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

with open("./telemetry.bin", "rb") as telem:
    # while (telem.peek(1) != b""):
    header = telem.read(24)

    # [uint16,uint8,uint8,uint8,uint8,uint64,float32,uint32,uint8,uint8]
    sep = struct.unpack("HBBBBfIBB", header)

    print(sep)
