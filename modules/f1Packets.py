import struct

eventSize = {
    "SSTA": 0, "SEND": 0, "FTLP": 5, "RTMT": 1, "DRSE": 0, "DRSD": 0, "TMPT": 1, "CHQF": 0, "RCWN": 1,
    "PENA": 7, "SPTP": 12, "STLG": 1, "LGOT": 0, "DTSV": 1, "SGSV": 1, "FLBK": 8, "BUTN": 4
}

packetSize = [1464, 632, 972, 40, 1257, 1102, 1347, 1058, 1015, 1191, 948, 1155]


def prepare(self, header, body):
    # Import Header values into packet
    for attr, value in header.__dict__.items():
        self.__dict__[attr] = value
    # Check Size
    if (len(body) + 24) != packetSize[self.type]:
        raise ValueError(f"Packet type {header.type} has size {len(body) + 24}. Should be {packetSize[self.type]}")


class Header():
    def __init__(self, header):
        self.format = header[0]
        self.game_version = f"{str(header[1])}.{str(header[2])}"
        self.version = header[3]
        self.type = header[4]
        self.session = header[5]
        self.timestamp = header[6]
        self.frame = header[7]
        self.p1car = header[8]
        self.p2car = header[9]


class EventPacket():
    def __init__(self, header, body):
        # Prepare packet values
        prepare(self, header, body)
        # Process body
        self.event = struct.unpack("4s", body[0:4])[0].decode("utf-8")
        self.body = body[4:]

    def __str__(self):
        return(f"{self.timestamp}: {self.event}: {self.body}")
