from fastapi import FastAPI
from pydantic import BaseModel
import datetime

app = FastAPI()

class EnergyData(BaseModel):
    meter_id: int
    V1: float
    V2: float
    V3: float
    I1: float
    I2: float
    I3: float
    P_total: float
    kWh_total: float

@app.get("/")
def home():
    return {"status": "ENTES Energy Platform running"}

@app.post("/data")
def receive_data(data: EnergyData):
    return {
        "message": "Data received",
        "timestamp": datetime.datetime.now(),
        "data": data
    }
