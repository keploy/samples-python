"""
Minimal FastAPI + SQLAlchemy + psycopg2 app that exercises the Postgres
v3 dispatcher's simple-query ClassCatalog branch via SQLAlchemy's
``Base.metadata.create_all`` table-existence probe.

Boot sequence:
  1. SQLAlchemy creates an engine over psycopg2. psycopg2 sends queries
     via the simple-Query protocol (``Q`` packet) even when the source
     SQL is parameterized: it does client-side ``%(param)s`` substitution
     and emits the resulting string as a single inlined statement
     (no ``Bind``/``Execute`` frames).
  2. ``Base.metadata.create_all(engine)`` issues one
     ``SELECT pg_catalog.pg_class.relname ...`` probe per declared table
     to decide whether each ``CREATE TABLE`` should be skipped. The
     probe SQL has 7 parameters (table name, relkind chars, namespace);
     psycopg2 inlines them before the wire write, so the dispatcher sees
     a simple-Query statement that classifies as ``ClassCatalog``.
  3. FastAPI starts serving requests.

The probe is what hits the dispatcher's ``case match.ClassCatalog``
branch in ``pkg/postgres/v3/replayer/dispatcher/dispatcher.go``
(simple-query path, ``dispatchBySQLHash``).
"""

import asyncio
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

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is required (e.g. postgresql+psycopg2://user:pass@host:5432/db). "
        "Set it in docker-compose env or in the host shell before launching uvicorn."
    )
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


# SQLAlchemy 2.x defaults to the future-2.0 behaviour, so no
# `future=True` is needed (and passing it can trip a deprecation
# warning depending on the installed minor version).
engine = create_engine(DATABASE_URL, echo=SQL_ECHO)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Wrap the startup work AND the yield in try/finally so
    # engine.dispose() runs even when create_all raises — which is
    # the exact failure mode this repro is built around (pre-fix
    # keploy makes create_all issue an unrecorded CREATE TABLE that
    # raises psycopg2.DatabaseError mid-startup; without the wrap,
    # the connection pool would leak on every replay attempt).
    try:
        log.info("startup: running Base.metadata.create_all (pg_class probe expected)")
        # create_all does synchronous psycopg2 I/O. Offload to a thread
        # so uvicorn's event loop stays responsive (otherwise any other
        # async work scheduled on startup would block until the pg_class
        # probe + any CREATE TABLE round-trips complete). For this
        # minimal repro the difference is small, but the pattern is the
        # right FastAPI shape for any startup that touches a sync DB
        # driver.
        await asyncio.to_thread(Base.metadata.create_all, engine)
        log.info("startup: create_all complete")
        yield
    finally:
        # Release pooled connections on shutdown so repeated
        # start/stop cycles (local repro loops, CI lanes) don't leak
        # half-open connections to postgres.
        engine.dispose()
        log.info("shutdown: engine pool disposed")


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/projects")
def list_projects():
    with Session(engine) as s:
        rows = s.execute(select(Project)).scalars().all()
        return [{"id": r.id, "name": r.name} for r in rows]
