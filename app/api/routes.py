import json
import asyncio

from fastapi import Depends, UploadFile, File, Form, Request
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.config.log import create_logger
from app.config.sse import sse_manager
from app.api.api import app
from app.db.connect import get_session
from app.api.operations import selects, inserts, updates
from app.util import enums
from app.api import models


log = create_logger()


async def event_stream(request: Request, channel: str):
    q = await sse_manager.subscribe(channel)
    try:
        while True:
            if await request.is_disconnected():
                break
            try:
                data = await asyncio.wait_for(q.get(), timeout=15)
                yield f"data: {data}\n\n"
            except asyncio.TimeoutError:
                yield ": keepalive\n\n"
    finally:
        sse_manager.unsubscribe(channel, q)


@app.get("/", tags=["ADM"])
async def redirecionar_para_docs():
    return RedirectResponse(
        url=app.docs_url, status_code=307
    )


@app.get("/events/orders", tags=["Stream", "Tela Entrega", "Tela Clientes"])
async def orders_events(request: Request):
    """For the client-facing screen and the delivery tablet."""
    return StreamingResponse(
        event_stream(request, "orders"),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/products/categories", tags=["Tela Venda"])
async def list_categories(session: Session = Depends(get_session)):
    return selects.list_categories(session)


@app.get("/products", tags=["Tela Venda"])
async def list_products(session: Session = Depends(get_session)):
    return selects.list_products(session)


@app.get("/product/image/{id}", tags=["Tela Venda"])
async def product_image(id: int, session: Session = Depends(get_session)):
    return selects.list_product_image(session, int(id))


@app.get("/product/info/{id}", tags=["ADM"])
async def product_info(id: int, session: Session = Depends(get_session)):
    return selects.list_product_info(session, id)


@app.get("/orders", tags=["Tela Clientes"])
async def list_orders(session: Session = Depends(get_session)):
    return selects.list_orders(session)


@app.get("/orders/items", tags=["Tela Cozinha"])
async def list_orders_and_items(session: Session = Depends(get_session)):
    return selects.list_orders_items(session)


@app.get("/stocks", tags=["ADM"])
async def list_stock(session: Session = Depends(get_session)):
    return selects.list_stock(session)


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
    return inserts.create_product(
        session, name,  category, 
        price, priority, file_bytes
    )


@app.post("/order", tags=["Tela Venda"])
async def create_order(
    order: models.NewOrder,
    session: Session = Depends(get_session)
):
    
    id = inserts.create_order_and_items(session, order)
    payload = json.dumps({"id": id, "status": enums.OrderStatus.queue.value})

    await sse_manager.publish("orders", payload)
    return {"id": id}


@app.post("/stock", tags=["ADM"])
async def create_stock_moviment(
    moviment: models.StockMoviment, 
    session: Session = Depends(get_session)
    ):
    return inserts.create_stock_moviment(session, moviment)


@app.patch("/order/{id}/{status}", tags=["Tela Cozinha", "Tela Entrega"])
async def alter_order(
        id: int, 
        status: enums.OrderStatus,
        session: Session = Depends(get_session)
    ):
    updates.alter_order_status(session, id, status)

    payload = json.dumps({"id": id, "status": status.value})

    await sse_manager.publish("orders", payload)

    return 
