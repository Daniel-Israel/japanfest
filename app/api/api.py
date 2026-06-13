from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import version
from app.db.connect import db
from app.config.log import configure_log
from app.queue.connect import get_channel


@asynccontextmanager
async def lifespan(app: FastAPI):

    configure_log()
    channel = get_channel()
    db.connect()

    yield
    channel.close()
    db.disconnect()


app = FastAPI(
        title="Backend da barraquinha de Fukushima",
        version=version,
        lifespan=lifespan
    )
