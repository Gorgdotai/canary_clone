"""Pydantic schemas for request and response payloads.

These classes define the shape of JSON data exchanged between clients
and the API.  Using Pydantic ensures proper validation and automatic
serialization.  Separate classes are defined for creating new
measurements (where the server generates an ID) and for reading
measurements back from the database (which include the ID field).
"""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class MeasurementCreate(BaseModel):
    """Schema for creating a measurement.

    Clients should provide the sensor identifier, timestamp and value.
    The timestamp must be provided in ISO 8601 format (e.g.
    "2025-07-25T15:30:00Z").
    """

    sensor_id: str = Field(..., example="sensor-1")
    ts: datetime = Field(..., example="2025-07-25T15:30:00Z")
    value: float = Field(..., example=42.0)


class MeasurementRead(BaseModel):
    """Schema for reading a measurement back to the client."""

    id: int
    sensor_id: str
    ts: datetime
    value: float

    class Config:
        orm_mode = True
