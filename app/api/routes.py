from fastapi import Depends, UploadFile, File, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config.log import create_logger
from app.api.api import app
from app.db.connect import get_session
from app.db import operations as bdaop
from app.db import orm


logger = create_logger()


@app.get("/")
async def redirecionar_para_docs():
    logger.error("erro")
    return RedirectResponse(
        url=app.docs_url, status_code=307
    )


@app.get("/products")
async def create_product(session: Session = Depends(get_session)):
    return bdaop.list_products(session)


@app.get("/product/image/{id}")
async def product_image(id: int, session: Session = Depends(get_session)):
    return bdaop.list_product_image(session, int(id))


@app.get("/product/info/{id}")
async def product_info(id: int, session: Session = Depends(get_session)):
    return bdaop.list_product_info(session, id)


@app.post("/product")
async def create_product(
        name: str = Form(...),
        category: str = Form(...),
        price: float = Form(...),
        priority: bool = Form(...),
        image_data: UploadFile = File(...),
        session: Session = Depends(get_session)
    ):
    file_bytes = await image_data.read()
    product = orm.Products(name=name, category=category, price=price, priority=priority, image_data=file_bytes)
    return bdaop.create_product(session, product)