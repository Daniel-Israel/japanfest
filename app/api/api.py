from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import version
from app.db.connect import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.connect()
    yield
    db.disconnect()


app = FastAPI(
        title="Backend da barraquinha de Fukushima",
        version=version,
        lifespan=lifespan
    )