from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="ENTES Energy Platform")

DATABASE_URL = os.getenv("DATABASE_URL")  # Railway otomatik verir (Postgres bağlıysa)

def get_conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL yok. Railway Postgres bağlı mı?")
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def ensure_table():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS meter_readings (
                id BIGSERIAL PRIMARY KEY,
                ts TIMESTAMPTZ NOT NULL,
                meter_id INT NOT NULL,
                v1 REAL, v2 REAL, v3 REAL,
                i1 REAL, i2 REAL, i3 REAL,
                p_total REAL,
                kwh_total REAL
            );
            """)
            conn.commit()
    finally:
        conn.close()

@app.on_event("startup")
def startup():
    # uygulama açılır açılmaz tabloyu oluştur
    ensure_table()

@app.get("/")
def root():
    return {"status": "ENTES Energy Platform running"}

class Reading(BaseModel):
    ts: str          # "2026-03-05T12:00:00Z" gibi
    meter_id: int
    v1: float | None = None
    v2: float | None = None
    v3: float | None = None
    i1: float | None = None
    i2: float | None = None
    i3: float | None = None
    p_total: float | None = None
    kwh_total: float | None = None

@app.post("/ingest")
def ingest(r: Reading):
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO meter_readings
                (ts, meter_id, v1, v2, v3, i1, i2, i3, p_total, kwh_total)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (r.ts, r.meter_id, r.v1, r.v2, r.v3, r.i1, r.i2, r.i3, r.p_total, r.kwh_total))
            conn.commit()
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            conn.close()
        except:
            pass

@app.get("/latest/{meter_id}")
def latest(meter_id: int):
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT ts, meter_id, v1, v2, v3, i1, i2, i3, p_total, kwh_total
                FROM meter_readings
                WHERE meter_id = %s
                ORDER BY ts DESC
                LIMIT 1
            """, (meter_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Kayıt yok")
            return row
    finally:
        conn.close()
