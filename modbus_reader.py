import os
import random
from dataclasses import dataclass
from typing import Dict, Any, Optional

from pymodbus.client import ModbusSerialClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian


@dataclass
class ModbusConfig:
    port: str = os.getenv("MODBUS_PORT", "COM5")
    baudrate: int = int(os.getenv("MODBUS_BAUDRATE", "19200"))
    parity: str = os.getenv("MODBUS_PARITY", "N")
    stopbits: int = int(os.getenv("MODBUS_STOPBITS", "1"))
    bytesize: int = int(os.getenv("MODBUS_BYTESIZE", "8"))
    timeout: float = float(os.getenv("MODBUS_TIMEOUT", "1.0"))
    unit_id: int = int(os.getenv("MODBUS_UNIT_ID", "1"))  # slave id


class MPR25S22Reader:
    """
    ENTES MPR-25S-22 (MPR-2X series) Modbus register map (Holding Registers):
      - V1: addr 0,  uint32, scale 0.1 V
      - V2: addr 2,  uint32, scale 0.1 V
      - V3: addr 4,  uint32, scale 0.1 V
      - I1: addr 14, uint32, unit mA, scale 0.001 => A
      - I2: addr 16, uint32, unit mA, scale 0.001 => A
      - I3: addr 18, uint32, unit mA, scale 0.001 => A
      - P_total (ΣActive Power +/-): addr 38, float32 (2 regs), W
      - Wh_total_consumed (Total Consumed Energy L1..L3): addr 216, uint64 (4 regs), Wh
    """

    def __init__(self, cfg: ModbusConfig, simulation: bool = True):
        self.cfg = cfg
        self.simulation = simulation

        self.client = ModbusSerialClient(
            port=cfg.port,
            baudrate=cfg.baudrate,
            parity=cfg.parity,
            stopbits=cfg.stopbits,
            bytesize=cfg.bytesize,
            timeout=cfg.timeout,
        )

    # ---------- low level helpers ----------

    def _read_holding(self, address: int, count: int):
        rr = self.client.read_holding_registers(address=address, count=count, slave=self.cfg.unit_id)
        if rr is None or rr.isError():
            return None
        return rr.registers

    @staticmethod
    def _decode_u32(registers) -> int:
        dec = BinaryPayloadDecoder.fromRegisters(
            registers, byteorder=Endian.BIG, wordorder=Endian.BIG
        )
        return dec.decode_32bit_uint()

    @staticmethod
    def _decode_u64(registers) -> int:
        dec = BinaryPayloadDecoder.fromRegisters(
            registers, byteorder=Endian.BIG, wordorder=Endian.BIG
        )
        return dec.decode_64bit_uint()

    @staticmethod
    def _decode_f32(registers) -> float:
        dec = BinaryPayloadDecoder.fromRegisters(
            registers, byteorder=Endian.BIG, wordorder=Endian.BIG
        )
        return float(dec.decode_32bit_float())

    # ---------- public ----------

    def connect(self) -> bool:
        if self.simulation:
            return True
        return bool(self.client.connect())

    def close(self):
        try:
            self.client.close()
        except Exception:
            pass

    def read_meter(self) -> Dict[str, Any]:
        # Simulation (cihaz yokken Railway/PC çökmesin)
        if self.simulation:
            v1 = round(random.uniform(215.0, 235.0), 1)
            v2 = round(random.uniform(215.0, 235.0), 1)
            v3 = round(random.uniform(215.0, 235.0), 1)
            i1 = round(random.uniform(0.0, 50.0), 3)
            i2 = round(random.uniform(0.0, 50.0), 3)
            i3 = round(random.uniform(0.0, 50.0), 3)
            p_total = round((v1 * i1 + v2 * i2 + v3 * i3) * random.uniform(0.7, 1.0), 2)
            kwh_total = round(random.uniform(0.0, 50000.0), 3)

            return {
                "ok": True,
                "simulation": True,
                "V1": v1,
                "V2": v2,
                "V3": v3,
                "I1": i1,
                "I2": i2,
                "I3": i3,
                "P_total_W": p_total,
                "kWh_total": kwh_total,
            }

        if not self.connect():
            return {"ok": False, "error": "Modbus connect failed", "simulation": False}

        # Voltages: uint32, scale 0.1V
        regs = self._read_holding(0, 2)
        if regs is None:
            return {"ok": False, "error": "Read V1 failed", "simulation": False}
        v1 = self._decode_u32(regs) * 0.1

        regs = self._read_holding(2, 2)
        if regs is None:
            return {"ok": False, "error": "Read V2 failed", "simulation": False}
        v2 = self._decode_u32(regs) * 0.1

        regs = self._read_holding(4, 2)
        if regs is None:
            return {"ok": False, "error": "Read V3 failed", "simulation": False}
        v3 = self._decode_u32(regs) * 0.1

        # Currents: uint32, unit mA, multiplier 0.001 => A
        regs = self._read_holding(14, 2)
        if regs is None:
            return {"ok": False, "error": "Read I1 failed", "simulation": False}
        i1 = self._decode_u32(regs) * 0.001

        regs = self._read_holding(16, 2)
        if regs is None:
            return {"ok": False, "error": "Read I2 failed", "simulation": False}
        i2 = self._decode_u32(regs) * 0.001

        regs = self._read_holding(18, 2)
        if regs is None:
            return {"ok": False, "error": "Read I3 failed", "simulation": False}
        i3 = self._decode_u32(regs) * 0.001

        # Total active power ΣP: float32, W
        regs = self._read_holding(38, 2)
        if regs is None:
            return {"ok": False, "error": "Read P_total failed", "simulation": False}
        p_total_w = self._decode_f32(regs)

        # Total consumed energy: uint64 Wh (4 regs) -> kWh
        regs = self._read_holding(216, 4)
        if regs is None:
            return {"ok": False, "error": "Read energy failed", "simulation": False}
        wh_total = self._decode_u64(regs)
        kwh_total = wh_total / 1000.0

        return {
            "ok": True,
            "simulation": False,
            "V1": round(v1, 3),
            "V2": round(v2, 3),
            "V3": round(v3, 3),
            "I1": round(i1, 6),
            "I2": round(i2, 6),
            "I3": round(i3, 6),
            "P_total_W": round(p_total_w, 3),
            "kWh_total": round(kwh_total, 6),
        }
