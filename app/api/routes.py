from fastapi import Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config.log import create_logger
from app.api.api import app
from app.db.connect import get_session


logger = create_logger()


@app.get("/")
async def redirecionar_para_docs():
    logger.error("erro")
    return RedirectResponse(
        url=app.docs_url, status_code=307
    )


@app.get("/teste")
async def teste(session: Session = Depends(get_session)):
    pass