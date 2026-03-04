# modbus_reader.py
# Cihaz yokken bile sistem çalışsın diye SIMULATION=True bırak.
# Cihaz geldiğinde SIMULATION=False yapacağız.

import random
from datetime import datetime

from pymodbus.client import ModbusSerialClient

# ================== AYARLAR ==================
SIMULATION = True          # cihaz yokken True kalsın
PORT = "COM5"              # senin USB-RS485 portun
BAUDRATE = 19200           # senin hızın (Entes ayarına göre)
PARITY = "N"
STOPBITS = 1
BYTESIZE = 8
TIMEOUT = 1

# Entes için örnek register adresleri (senin modeline göre değişebilir)
# Burada sadece demo amaçlı 4 değer okuyormuş gibi yaptık.
REG_VOLTAGE = 0x0000
REG_CURRENT = 0x0006
REG_POWER   = 0x0034
REG_ENERGY  = 0x0156

# ================== CLIENT ==================
client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    parity=PARITY,
    stopbits=STOPBITS,
    bytesize=BYTESIZE,
    timeout=TIMEOUT
)

def _safe_float(val, default=None):
    try:
        return float(val)
    except Exception:
        return default

def _simulated_meter(slave_id: int):
    # cihaz yokken rastgele ama mantıklı değerler üret
    v = round(random.uniform(220.0, 235.0), 1)
    i = round(random.uniform(0.0, 20.0), 2)
    p = round(v * i * random.uniform(0.7, 1.0), 1)
    e = round(random.uniform(1000.0, 50000.0), 2)
    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "slave_id": slave_id,
        "voltage": v,
        "current": i,
        "power": p,
        "energy": e,
        "mode": "SIMULATION"
    }

def read_meter(slave_id: int):
    """
    Tek cihaz okur. SIMULATION=True ise cihaz bağlanmadan veri üretir.
    """
    if SIMULATION:
        return _simulated_meter(slave_id)

    if not client.connect():
        return {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "slave_id": slave_id,
            "error": "Modbus bağlantısı kurulamadı (client.connect() false)",
            "mode": "REAL"
        }

    try:
        # Her biri 2 register okuyor gibi örnek (cihaz modeline göre değişebilir)
        r_v = client.read_input_registers(REG_VOLTAGE, 2, slave=slave_id)
        r_i = client.read_input_registers(REG_CURRENT, 2, slave=slave_id)
        r_p = client.read_input_registers(REG_POWER,   2, slave=slave_id)
        r_e = client.read_input_registers(REG_ENERGY,  2, slave=slave_id)

        # Basit dönüşüm (gerçekte ölçekleme/float formatı modele göre değişebilir)
        v = r_v.registers[0] if (r_v and not r_v.isError()) else None
        i = r_i.registers[0] if (r_i and not r_i.isError()) else None
        p = r_p.registers[0] if (r_p and not r_p.isError()) else None
        e = r_e.registers[0] if (r_e and not r_e.isError()) else None

        return {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "slave_id": slave_id,
            "voltage": _safe_float(v),
            "current": _safe_float(i),
            "power": _safe_float(p),
            "energy": _safe_float(e),
            "mode": "REAL"
        }

    except Exception as ex:
        return {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "slave_id": slave_id,
            "error": f"Okuma hatası: {ex}",
            "mode": "REAL"
        }
    finally:
        try:
            client.close()
        except Exception:
            pass


if __name__ == "__main__":
    # Test: 1. cihazı oku
    print(read_meter(1))
