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
        self.cars = []
        for _ in range(22):
            car = list(struct.unpack("=6f6h6f", body[0:60]))
            for i, x in enumerate(car[6:12]):
                car[i+6] = x / 32767.0
            self.cars.append(tuple(car))
            body = body[60:]
        self.motion = struct.unpack("=15f", body[0:60])


class SessionPacket(Packet):
    def __init__(self, header, body):
        super().__init__(header, body)
        (
            self.weather, self.trackTemp, self.airTemp, self.totalLaps,
            self.trackLength, self.seshType, self.trackId, self.formula,
            self.seshTimeLeft, self.seshDuration, self.pitSpeed, self.paused,
            self.spectating, self.spectIndex, self.sli, self.marshalZoneCount
        ) = struct.unpack("=B2bBHBbB2H6B", body[0:19])
        body = body[19:]
        zones = []
        for _ in range(21):
            zones.append(struct.unpack("=fb", body[0:5]))
            body = body[5:]
        (self.safetyCar, self.network, self.forecastSampleCount) = struct.unpack("=3B", body[0:3])
        body = body[3:]
        forecast = []
        for _ in range(56):
            forecast.append(struct.unpack("=3B4bB", body[0:8]))
            body = body[8:]
        (
            self.forecastAccuracy, self.aiDifficulty, self.seasonLinkId, self.weekendLinkId,
            self.sessionLinkId, self.pitIdeal, self.pitLatest, self.pitRejoin
        ) = struct.unpack("=2B3L3B", body[0:17])
        body = body[17:]
        self.assists = struct.unpack("=9B", body[0:9])
        body = body[9:]
        (
            self.mode, self.rules, localTime, self.seshLength
        ) = struct.unpack("=2BLB", body[0:7])
        self.localTime = f"{localTime // 60}:{localTime % 60 :02d}"


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
        self.count = struct.unpack("B", body[0:1])[0]
        body = body[1:]
        self.cars = []
        for _ in range(22):
            participant = list(struct.unpack("=7B48sB", body[0:56]))
            participant[7] = participant[7].strip(b'\x00').decode("utf-8")
            self.cars.append(tuple(participant))
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
