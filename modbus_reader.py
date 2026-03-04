class ModbusConfig:
    def __init__(self, port, baudrate, parity, stopbits, bytesize, timeout, unit_id):
        self.port = port
        self.baudrate = baudrate
        self.parity = parity
        self.stopbits = stopbits
        self.bytesize = bytesize
        self.timeout = timeout
        self.unit_id = unit_id


class MPR25S22Reader:
    def __init__(self, cfg, simulation=True):
        self.cfg = cfg
        self.simulation = simulation

    def read_meter(self):
        return {
            "ok": True,
            "simulation": True,
            "V1": 230,
            "V2": 231,
            "V3": 229,
            "I1": 10,
            "I2": 11,
            "I3": 9,
            "P_total_W": 5000,
            "kWh_total": 12000
        }
