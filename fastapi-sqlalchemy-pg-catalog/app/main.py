"""
Minimal FastAPI + SQLAlchemy + psycopg2 app that exercises the Postgres
v3 dispatcher's simple-query ClassCatalog branch via SQLAlchemy's
``Base.metadata.create_all`` table-existence probe.

Boot sequence:
  1. SQLAlchemy creates an engine over psycopg2 (simple-query for
     parameter-less SQL).
  2. ``Base.metadata.create_all(engine)`` issues one
     ``SELECT pg_catalog.pg_class.relname ...`` probe per declared table
     to decide whether each ``CREATE TABLE`` should be skipped.
  3. FastAPI starts serving requests.

The probe is what hits the dispatcher's ``case match.ClassCatalog``
branch in ``pkg/postgres/v3/replayer/dispatcher/dispatcher.go``
(simple-query path, ``dispatchBySQLHash``).
"""

import logging
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import Column, Integer, String, create_engine, select
from sqlalchemy.orm import Session, declarative_base

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("repro")

DATABASE_URL = os.environ["DATABASE_URL"]
# SQL echo is INTENTIONALLY on by default — this is a sample for
# demonstrating the dispatcher's simple-Query catalog path, and seeing
# the actual SQLAlchemy queries (pg_catalog.version, pg_class probe,
# CREATE TABLE on miss) in the app log is the load-bearing observation
# that lets a reader correlate the keploy agent log with what the app
# is doing. The trade-off: SQLAlchemy logs every statement at INFO,
# which is verbose in normal operation. Override SQL_ECHO=0 to quiet
# it down for unrelated investigations.
SQL_ECHO = os.environ.get("SQL_ECHO", "1") != "0"

Base = declarative_base()


class Project(Base):
    __tablename__ = "project"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)


engine = create_engine(DATABASE_URL, echo=SQL_ECHO, future=True)


@asynccontextmanager
async def lifespan(_: FastAPI):
    log.info("startup: running Base.metadata.create_all (pg_class probe expected)")
    Base.metadata.create_all(engine)
    log.info("startup: create_all complete")
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/projects")
def list_projects():
    with Session(engine) as s:
        rows = s.execute(select(Project)).scalars().all()
        return [{"id": r.id, "name": r.name} for r in rows]
