import os
import random
from datetime import datetime

from pymodbus.client import ModbusSerialClient

# Railway'de cihaz olmayacağı için varsayılan SIMULATION=1
SIMULATION = os.getenv("SIMULATION", "1") == "1"

# Lokal PC'de (senin) COM port
PORT = os.getenv("MODBUS_PORT", "COM5")
BAUDRATE = int(os.getenv("MODBUS_BAUD", "19200"))


def _fake(slave_id: int):
    # Simülasyon değerleri
    return {
        "ts": datetime.utcnow().isoformat() + "Z",
        "meter_id": slave_id,
        "mode": "simulation",
        "V1": round(random.uniform(215, 235), 1),
        "V2": round(random.uniform(215, 235), 1),
        "V3": round(random.uniform(215, 235), 1),
        "I1": round(random.uniform(0, 50), 2),
        "I2": round(random.uniform(0, 50), 2),
        "I3": round(random.uniform(0, 50), 2),
        "P_total": round(random.uniform(0, 25), 3),
        "kWh_total": round(random.uniform(1000, 50000), 2),
    }


def read_meter(slave_id: int):
    if SIMULATION:
        return _fake(slave_id)

    client = ModbusSerialClient(
        port=PORT,
        baudrate=BAUDRATE,
        parity="N",
        stopbits=1,
        bytesize=8,
        timeout=1,
    )

    if not client.connect():
        return {
            "ts": datetime.utcnow().isoformat() + "Z",
            "meter_id": slave_id,
            "mode": "real",
            "error": f"Modbus connect failed (PORT={PORT}, BAUDRATE={BAUDRATE})",
        }

    try:
        # ⚠️ Bu adresler örnektir. Senin ENTES modeline göre register adreslerini netleştireceğiz.
        # Şimdilik hata vermeden çalışması için "okuma denemesi" yapıyoruz:
        r = client.read_input_registers(0x0000, 2, slave=slave_id)

        return {
            "ts": datetime.utcnow().isoformat() + "Z",
            "meter_id": slave_id,
            "mode": "real",
            "raw": getattr(r, "registers", None),
        }
    finally:
        client.close()
