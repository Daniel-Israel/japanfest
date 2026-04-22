from fastapi import Depends, UploadFile, File, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config.log import create_logger
from app.api.api import app
from app.db.connect import get_session
from app.db import operations as bdops
from app.api import operations as apiops
from app.util import enums
from app.api import models


logger = create_logger()


@app.get("/", tags=["ADM"])
async def redirecionar_para_docs():
    logger.error("erro")
    return RedirectResponse(
        url=app.docs_url, status_code=307
    )


@app.get("/products/categories", tags=["Tela Venda"])
async def list_categories(session: Session = Depends(get_session)):
    return bdops.list_categories(session)


@app.get("/products", tags=["Tela Venda"])
async def list_products(session: Session = Depends(get_session)):
    return bdops.list_products(session)


@app.get("/product/image/{id}", tags=["Tela Venda"])
async def product_image(id: int, session: Session = Depends(get_session)):
    return bdops.list_product_image(session, int(id))


@app.get("/product/info/{id}", tags=["ADM"])
async def product_info(id: int, session: Session = Depends(get_session)):
    return bdops.list_product_info(session, id)


@app.get("/orders", tags=["Tela Clientes"])
async def list_orders(session: Session = Depends(get_session)):
    return bdops.list_orders(session)


@app.get("/orders/items", tags=["Tela Cozinha"])
async def list_orders_and_items(session: Session = Depends(get_session)):
    return bdops.list_orders_items(session)


@app.post("/product", tags=["ADM"])
async def create_product(
        name: str = Form(...),
        category: str = Form(...),
        price: float = Form(...),
        priority: bool = Form(...),
        image_data: UploadFile = File(...),
        session: Session = Depends(get_session)
    ):
    file_bytes = await image_data.read()
    return apiops.create_product(
        session, name,  category, 
        price, priority, file_bytes
    )


@app.post("/order", tags=["Tela Venda"])
async def create_order(
    order: models.NewOrder,
    session: Session = Depends(get_session)
):
    return apiops.create_order_and_items(session, order)


@app.post("/stock", tags=["ADM"])
async def create_stock_moviment(
    moviment: models.StockMoviment, 
    session: Session = Depends(get_session)
    ):
    return apiops.create_stock_moviment(session, moviment)


@app.patch("/order/{id}/{status}", tags=["Tela Cozinha", "Tela Entrega"])
async def alter_order(
        id: int, 
        status: enums.OrderStatus,
        session: Session = Depends(get_session)
    ):
    return bdops.alter_order_status(session, id, status)

