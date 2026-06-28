from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import version
from app.db.connect import db
from app.config.log import configure_log
from app.print.printer import connect_printer


@asynccontextmanager
async def lifespan(app: FastAPI):

    configure_log()
    db.connect()
    connect_printer()
    yield
    db.disconnect()


app = FastAPI(
        title="Backend da barraquinha de Fukushima",
        version=version,
        lifespan=lifespan
    )
