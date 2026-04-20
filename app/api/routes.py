from app import version

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.config.log import create_logger


app = FastAPI(
        title="Backend da barraquinha de Fukushima",
        version=version
    )
logger = create_logger()


@app.get("/")
async def redirecionar_para_docs():
    logger.error("erro")
    return RedirectResponse(
        url=app.docs_url, status_code=307
    )
