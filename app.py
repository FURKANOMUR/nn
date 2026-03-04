from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import random
import datetime

app = FastAPI(title="ENTES Energy Platform")

SIMULATION = True


def fake_meter(mid):
    return {
        "meter_id": mid,
        "V1": random.randint(228, 232),
        "V2": random.randint(228, 232),
        "V3": random.randint(228, 232),
        "I1": random.randint(5, 20),
        "I2": random.randint(5, 20),
        "I3": random.randint(5, 20),
        "P_total_W": random.randint(2000, 8000),
        "kWh_total": random.randint(10000, 50000),
    }


@app.get("/")
def root():
    return {"status": "ENTES Energy Platform running", "simulation": True}


@app.get("/meter/{meter_id}")
def meter(meter_id: int):
    return fake_meter(meter_id)


@app.get("/meters")
def meters():
    data = []
    for i in range(1, 18):
        data.append(fake_meter(i))

    return {
        "ok": True,
        "meters": data,
        "timestamp": datetime.datetime.now().isoformat()
    }


@app.get("/ui", response_class=HTMLResponse)
def ui():

    return """
    <html>
    <head>
    <title>ENTES Energy Dashboard</title>

    <style>
    body{
        font-family:Arial;
        background:#0f172a;
        color:white;
        padding:40px;
    }

    h1{
        margin-bottom:30px;
    }

    table{
        width:100%;
        border-collapse:collapse;
        background:#1e293b;
    }

    th,td{
        padding:10px;
        border-bottom:1px solid #334155;
        text-align:center;
    }

    th{
        background:#334155;
    }

    </style>

    </head>

    <body>

    <h1>ENTES Energy Dashboard</h1>

    <table id="table">
    <tr>
    <th>Meter</th>
    <th>V1</th>
    <th>V2</th>
    <th>V3</th>
    <th>I1</th>
    <th>I2</th>
    <th>I3</th>
    <th>Power (W)</th>
    <th>Energy (kWh)</th>
    </tr>
    </table>

    <script>

    async function load(){

        let r = await fetch('/meters')
        let data = await r.json()

        let table = document.getElementById("table")

        data.meters.forEach(m=>{

            let row = table.insertRow()

            row.insertCell().innerText = m.meter_id
            row.insertCell().innerText = m.V1
            row.insertCell().innerText = m.V2
            row.insertCell().innerText = m.V3
            row.insertCell().innerText = m.I1
            row.insertCell().innerText = m.I2
            row.insertCell().innerText = m.I3
            row.insertCell().innerText = m.P_total_W
            row.insertCell().innerText = m.kWh_total

        })

    }

    load()

    </script>

    </body>
    </html>
    """
