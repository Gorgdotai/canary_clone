"""Database setup for the Canary clone project.

This module configures an SQLite database using SQLAlchemy.  A single
`measurements` table is defined for storing time‑series sensor data.  Each
record captures the sensor identifier, the timestamp of the reading and
the numeric value reported.  SQLAlchemy’s ORM is used to abstract
database interactions.

The database URL defaults to an SQLite file stored in the project
directory.  If the environment variable `DATABASE_URL` is set it will
override the default.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Float, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Resolve the database URL from the environment or default to a local file.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./canary.db")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Measurement(Base):
    """ORM model for a sensor measurement.

    Each measurement stores a unique integer primary key, the sensor identifier as
    a string, the timestamp of the reading, and the measured value.  A simple
    schema like this is sufficient for a proof‑of‑concept data historian.  In
    production one might normalise sensors and devices into separate tables and
    introduce foreign keys.
    """

    __tablename__ = "measurements"

    id: int = Column(Integer, primary_key=True, index=True)
    sensor_id: str = Column(String, index=True)
    ts: datetime = Column(DateTime, index=True)
    value: float = Column(Float)


def init_db() -> None:
    """Create database tables.

    Calling this function will create all tables declared by the Base
    subclasses.  It is idempotent – existing tables will not be
    re‑created.  Run this at application start to ensure the schema
    exists.
    """
    Base.metadata.create_all(bind=engine)
