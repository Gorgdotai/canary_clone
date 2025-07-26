from __future__ import annotations
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Depends, Request, Query, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

# Import your DB logic and schemas
from database import SessionLocal, init_db, Measurement
from schemas import MeasurementCreate, MeasurementRead

# ✅ Initialize app
app = FastAPI(
    title="Canary Clone API",
    description="A minimal open‑source replacement for the Canary data collector."
)

# ✅ Mount static files (for sounds, images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ Templates for rendering HTML
templates = Jinja2Templates(directory="templates")


# ✅ Homepage route (serves Donut Clicker UI)
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ✅ Startup event to initialize DB
@app.on_event("startup")
def startup():
    init_db()


# ✅ Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ API Endpoints
@app.post("/measurements", response_model=MeasurementRead, status_code=status.HTTP_201_CREATED)
def create_measurement(measurement: MeasurementCreate, db: Session = Depends(get_db)) -> MeasurementRead:
    record = Measurement(sensor_id=measurement.sensor_id, ts=measurement.ts, value=measurement.value)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.get("/measurements", response_model=List[MeasurementRead])
def read_measurements(
    sensor_id: str = Query(..., description="Sensor identifier"),
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    limit: int = 1000,
    db: Session = Depends(get_db),
) -> List[MeasurementRead]:
    query = db.query(Measurement).filter(Measurement.sensor_id == sensor_id)
    if start:
        query = query.filter(Measurement.ts >= start)
    if end:
        query = query.filter(Measurement.ts < end)
    return query.order_by(Measurement.ts.asc()).limit(limit).all()


@app.get("/sensors", response_model=List[str])
def list_sensors(db: Session = Depends(get_db)) -> List[str]:
    results = db.query(Measurement.sensor_id).distinct().all()
    return [row[0] for row in results]


# ✅ Run locally
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
