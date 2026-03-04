from fastapi import FastAPI, HTTPException
import modbus_reader

app = FastAPI(title="ENTES Energy Platform")

@app.get("/")
def root():
    return {"status": "ENTES Energy Platform running"}

@app.get("/health")
def health():
    return {"ok": True, "simulation": modbus_reader.SIMULATION}

@app.get("/meter/{slave_id}")
def meter(slave_id: int):
    try:
        return modbus_reader.read_meter(slave_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
