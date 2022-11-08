import struct

eventSize = {
    "SSTA": 0, "SEND": 0, "FTLP": 5, "RTMT": 1, "DRSE": 0, "DRSD": 0, "TMPT": 1, "CHQF": 0, "RCWN": 1,
    "PENA": 7, "SPTP": 12, "STLG": 1, "LGOT": 0, "DTSV": 1, "SGSV": 1, "FLBK": 8, "BUTN": 4
}

packetSize = [1464, 632, 972, 40, 1257, 1102, 1347, 1058, 1015, 1191, 948, 1155]

# Tyre Indices
RL = 0
RR = 1
FL = 2
FR = 3


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


class Data():
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
        self.body = Data(body)

    def __str__(self):
        return(f"{self.timestamp}: {self.body.values}")


class CarMotion():
    def __init__(self, data):
        (
            self.wpx, self.wpy, self.wpz,
            self.wvx, self.wvy, self.wvz
        ) = data[0:6]
        (
            self.fwdx, self.fwdy, self.fwdz,
            self.rgtx, self.rgty, self.rgtz
        ) = [x / 32767.0 for x in data[6:12]]
        (
            self.glat, self.glon, self.gver,
            self.yaw, self.pitch, self.roll
        ) = data[12:18]


class MotionPacket(Packet):
    def __init__(self, header, body):
        super().__init__(header, body)
        self.cars = []
        for _ in range(22):
            self.cars.append(CarMotion(struct.unpack("=6f6h6f", self.body.read(60))))
        self.motion = struct.unpack("=15f", self.body.read(60))


class MarshalZone():
    def __init__(self, data):
        self.start = data[0]
        self.flag = data[1]


class Forecast():
    def __init__(self, data):
        (
            self.session, self.offset, self.weather, self.trackTemp,
            self.trackTempDelta, self.airTemp, self.airTempDelta, self.rainChance
        ) = data


class SessionPacket(Packet):
    def __init__(self, header, body):
        super().__init__(header, body)
        (
            self.weather, self.trackTemp, self.airTemp, self.totalLaps,
            self.trackLength, self.seshType, self.trackId, self.formula,
            self.seshTimeLeft, self.seshDuration, self.pitSpeed, self.paused,
            self.spectating, self.spectIndex, self.sli, self.marshalZoneCount
        ) = struct.unpack("=B2bBHBbB2H6B", self.body.read(19))
        self.zones = []
        for _ in range(21):
            self.zones.append(MarshalZone(struct.unpack("=fb", self.body.read(5))))
        (self.safetyCar, self.network, self.forecastSampleCount) = struct.unpack("=3B", self.body.read(3))
        self.forecast = []
        for _ in range(56):
            self.forecast.append(Forecast(struct.unpack("=3B4bB", self.body.read(8))))
        (
            self.forecastAccuracy, self.aiDifficulty, self.seasonLinkId, self.weekendLinkId,
            self.sessionLinkId, self.pitIdeal, self.pitLatest, self.pitRejoin
        ) = struct.unpack("=2B3L3B", self.body.read(17))
        self.assists = struct.unpack("=9B", self.body.read(9))
        (
            self.mode, self.rules, localTime, self.seshLength
        ) = struct.unpack("=2BLB", self.body.read(7))
        self.localTime = f"{localTime // 60 :02d}:{localTime % 60 :02d}"


class CarLap():
    def __init__(self, data):
        (
            self.lastLap, self.curLap, self.sector1, self.sector2,
            self.lapDist, self.totalDist, self.safetyDelta, self.position,
            self.lap, self.pit, self.pits, self.sector,
            self.lapValid, self.penalties, self.warnings, self.driveThrus,
            self.stopGos, self.gridPos, self.status, self.result,
            self.pitLane, self.pitLaneTime, self.pitStopTime, self.pitServe 
        ) = data


class LapDataPacket(Packet):
    def __init__(self, header, body):
        super().__init__(header, body)
        self.cars = []
        for _ in range(22):
            self.cars.append(CarLap(struct.unpack("=2L2H3f14B2HB", self.body.read(43))))
        (self.ttPB, self.ttRiv) = struct.unpack("=2B", self.body.read(2))


class EventPacket(Packet):
    def __init__(self, header, body):
        super().__init__(header, body)
        self.event = struct.unpack("4s", self.body.read(4))[0].decode("utf-8")

    def __str__(self):
        return(f"{self.timestamp}: {self.event}, {self.body}")


class Participant():
    def __init__(self, data):
        (
            self.ai, self.driverID, self.networkID,
            self.teamID, self.myTeam, self.raceNum,
            self.nationality, self.name, self.udp
        ) = data
        self.name = self.name.strip(b'\x00').decode("utf-8")


class ParticipantPacket(Packet):
    def __init__(self, header, body):
        super().__init__(header, body)
        self.count = struct.unpack("B", self.body.read(1))[0]
        self.drivers = []
        for _ in range(22):
            self.drivers.append(Participant(struct.unpack("=7B48sB", self.body.read(56))))


class CarSetup():
    def __init__(self, data):
        self.tyrePressure = [None] * 4
        (
            self.frontWing, self.rearWing, self.onThrottle, self.offThrottle,
            self.frontCamber, self.rearCamber, self.frontToe, self.rearToe,
            self.frontSus, self.rearSus, self.frontRollbar, self.rearRollbar,
            self.frontHeight, self.rearHeight, self.brakePressure, self.brakeBias,
            self.tyrePressure[RL], self.tyrePressure[RR], self.tyrePressure[FL], self.tyrePressure[FR],
            self.ballast, self.fuelLoad
        ) = data


class SetupPacket(Packet):
    def __init__(self, header, body):
        super().__init__(header, body)
        self.cars = []
        for _ in range(22):
            self.cars.append(CarSetup(struct.unpack("=4B4f8B4fBf", self.body.read(49))))


class CarTelemetry():
    def __init__(self, data):
        self.brakeTemp = [None] * 4
        self.tyreSurface = [None] * 4
        self.tyreInner = [None] * 4
        self.tyrePressure = [None] * 4
        self.surfaceType = [None] * 4
        (
            self.speed, self.throttle, self.steer, self.brake,
            self.clutch, self.gear, self.rpm, self.drs,
            self.revLightsPercent, self.revLightsBitValue,
            self.brakeTemp[RL], self.brakeTemp[RR], self.brakeTemp[FL], self.brakeTemp[FR],
            self.tyreSurface[RL], self.tyreSurface[RR], self.tyreSurface[FL], self.tyreSurface[FR],
            self.tyreInner[RL], self.tyreInner[RR], self.tyreInner[FL], self.tyreInner[FR],
            self.engineTemp,
            self.tyrePressure[RL], self.tyrePressure[RR], self.tyrePressure[FL], self.tyrePressure[FR],
            self.surfaceType[RL], self.surfaceType[RR], self.surfaceType[FL], self.surfaceType[FR],
        ) = data


class TelemetryPacket(Packet):
    def __init__(self, header, body):
        super().__init__(header, body)
        self.cars = []
        for _ in range(22):
            self.cars.append(CarTelemetry(struct.unpack("=H3fBbH2B5H8BH4f4B", self.body.read(60))))
        (self.mfdP1, self.mfdP2, self.suggestedGear) = struct.unpack("2Bb", self.body.read(3))


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
