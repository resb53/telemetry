import struct

eventSize = {
    "SSTA": 0, "SEND": 0, "FTLP": 5, "RTMT": 1, "DRSE": 0, "DRSD": 0, "TMPT": 1, "CHQF": 0, "RCWN": 1,
    "PENA": 7, "SPTP": 12, "STLG": 1, "LGOT": 0, "DTSV": 1, "SGSV": 1, "FLBK": 8, "BUTN": 4
}

packetSize = [1464, 632, 972, 40, 1257, 1102, 1347, 1058, 1015, 1191, 948, 1155]


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


class Packet():
    def __init__(self, header, body):
        # Import Header values into packet
        for attr, value in header.__dict__.items():
            self.__dict__[attr] = value
        # Check Size
        if (len(body) + 24) != packetSize[self.type]:
            raise ValueError(f"Packet type {header.type} has size {len(body) + 24}. Should be {packetSize[self.type]}")
        self.body = body

    def __str__(self):
        return(f"{self.timestamp}: {self.body}")


class MotionPacket(Packet):
    def __init__(self, header, body):
        super().__init__(header, body)


class SessionPacket(Packet):
    def __init__(self, header, body):
        super().__init__(header, body)


class LapDataPacket(Packet):
    def __init__(self, header, body):
        super().__init__(header, body)


class EventPacket(Packet):
    def __init__(self, header, body):
        super().__init__(header, body)
        self.event = struct.unpack("4s", body[0:4])[0].decode("utf-8")
        self.body = body[4:]

    def __str__(self):
        return(f"{self.timestamp}: {self.event}, {self.body}")


class ParticipantPacket(Packet):
    def __init__(self, header, body):
        super().__init__(header, body)
        self.count = struct.unpack("B", body[0])
        body = body[1:]
        self.cars = []
        for _ in range(22):
            self.cars.append(struct.unpack("=7B48sB", body[0:56]))
            body = body[56:]


class SetupPacket(Packet):
    def __init__(self, header, body):
        super().__init__(header, body)


class TelemetryPacket(Packet):
    def __init__(self, header, body):
        super().__init__(header, body)


class StatusPacket(Packet):
    def __init__(self, header, body):
        super().__init__(header, body)
        self.cars = []
        for _ in range(22):
            self.cars.append(struct.unpack("=5B3f2H2BH3BbfB3fB", body[0:47]))
            body = body[47:]


class ClassificationPacket(Packet):
    def __init__(self, header, body):
        super().__init__(header, body)


class LobbyPacket(Packet):
    def __init__(self, header, body):
        super().__init__(header, body)


class DamagePacket(Packet):
    def __init__(self, header, body):
        super().__init__(header, body)


class HistoryPacket(Packet):
    def __init__(self, header, body):
        super().__init__(header, body)