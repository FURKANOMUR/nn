import os
from fastapi import FastAPI, HTTPException

from modbus_reader import ModbusConfig, MPR25S22Reader

app = FastAPI(title="ENTES Energy Platform")

# ENV ile kontrol:
# SIMULATION=true/false
SIMULATION = os.getenv("SIMULATION", "true").lower() in ("1", "true", "yes", "on")

cfg = ModbusConfig(
    port=os.getenv("MODBUS_PORT", "COM5"),
    baudrate=int(os.getenv("MODBUS_BAUDRATE", "19200")),
    parity=os.getenv("MODBUS_PARITY", "N"),
    stopbits=int(os.getenv("MODBUS_STOPBITS", "1")),
    bytesize=int(os.getenv("MODBUS_BYTESIZE", "8")),
    timeout=float(os.getenv("MODBUS_TIMEOUT", "1.0")),
    unit_id=int(os.getenv("MODBUS_UNIT_ID", "1")),
)

reader = MPR25S22Reader(cfg, simulation=SIMULATION)


@app.get("/")
def root():
    return {"status": "ENTES Energy Platform running", "simulation": SIMULATION}


@app.get("/health")
def health():
    return {"ok": True, "simulation": SIMULATION}


# Hem /meter/1 hem /meters/1 çalışsın diye ikisini de koydum:
@app.get("/meter/{meter_id}")
@app.get("/meters/{meter_id}")
def get_meter(meter_id: int):
    # Şimdilik tek cihaz okuyoruz: MODBUS_UNIT_ID üzerinden.
    # meter_id'yi ileride çoklu cihaz için kullanacağız.
    data = reader.read_meter()
    if not data.get("ok"):
        raise HTTPException(status_code=503, detail=data.get("error", "read failed"))
    data["meter_id"] = meter_id
    data["unit_id"] = cfg.unit_id
    return data
