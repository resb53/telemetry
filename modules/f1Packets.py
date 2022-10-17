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


class Body():
    def __init__(self, body):
        self.values = body
        self.index = 0
        self.length = len(body)

    def __len__(self):
        return self.length

    def read(self, n):
        if n > (self.length - self.index):
            raise IndexError(f"{n} bytes requested where only {self.length - self.index} remain")
        else:
            r = self.values[self.index:self.index+n]
            self.index += n
            return r

    def reset(self):
        self.index = 0


class Packet():
    def __init__(self, header, body):
        # Import Header values into packet
        for attr, value in header.__dict__.items():
            self.__dict__[attr] = value
        # Check Size
        if (len(body) + 24) != packetSize[self.type]:
            raise ValueError(f"Packet type {header.type} has size {len(body) + 24}. Should be {packetSize[self.type]}")
        self.body = Body(body)

    def __str__(self):
        return(f"{self.timestamp}: {self.body.values}")


class MotionPacket(Packet):
    def __init__(self, header, body):
        super().__init__(header, body)
        self.cars = []
        for _ in range(22):
            car = list(struct.unpack("=6f6h6f", self.body.read(60)))
            for i, x in enumerate(car[6:12]):
                car[i+6] = x / 32767.0
            self.cars.append(tuple(car))
        self.motion = struct.unpack("=15f", self.body.read(60))


class SessionPacket(Packet):
    def __init__(self, header, body):
        super().__init__(header, body)
        (
            self.weather, self.trackTemp, self.airTemp, self.totalLaps,
            self.trackLength, self.seshType, self.trackId, self.formula,
            self.seshTimeLeft, self.seshDuration, self.pitSpeed, self.paused,
            self.spectating, self.spectIndex, self.sli, self.marshalZoneCount
        ) = struct.unpack("=B2bBHBbB2H6B", self.body.read(19))
        zones = []
        for _ in range(21):
            zones.append(struct.unpack("=fb", self.body.read(5)))
        (self.safetyCar, self.network, self.forecastSampleCount) = struct.unpack("=3B", self.body.read(3))
        forecast = []
        for _ in range(56):
            forecast.append(struct.unpack("=3B4bB", self.body.read(8)))
        (
            self.forecastAccuracy, self.aiDifficulty, self.seasonLinkId, self.weekendLinkId,
            self.sessionLinkId, self.pitIdeal, self.pitLatest, self.pitRejoin
        ) = struct.unpack("=2B3L3B", self.body.read(17))
        self.assists = struct.unpack("=9B", self.body.read(9))
        (
            self.mode, self.rules, localTime, self.seshLength
        ) = struct.unpack("=2BLB", self.body.read(7))
        self.localTime = f"{localTime // 60 :02d}:{localTime % 60 :02d}"


class LapDataPacket(Packet):
    def __init__(self, header, body):
        super().__init__(header, body)
        self.cars = []


class EventPacket(Packet):
    def __init__(self, header, body):
        super().__init__(header, body)
        self.event = struct.unpack("4s", self.body.read(4))[0].decode("utf-8")

    def __str__(self):
        return(f"{self.timestamp}: {self.event}, {self.body}")


class ParticipantPacket(Packet):
    def __init__(self, header, body):
        super().__init__(header, body)
        self.count = struct.unpack("B", self.body.read(1))[0]
        self.cars = []
        for _ in range(22):
            participant = list(struct.unpack("=7B48sB", self.body.read(56)))
            participant[7] = participant[7].strip(b'\x00').decode("utf-8")
            self.cars.append(tuple(participant))


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
            self.cars.append(struct.unpack("=5B3f2H2BH3BbfB3fB", self.body.read(47)))


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
