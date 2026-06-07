import json
import asyncio
from typing import List, Optional

from fastapi import Depends, UploadFile, File, Form, Request, Query
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.config.log import create_logger
from app.config.sse import sse_manager
from app.api.api import app
from app.db.connect import get_session
from app.api.operations import selects, inserts, updates
from app.util import enums
from app.util.pix import create_pix_qr_code
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
async def redirect_docs():
    return RedirectResponse(
        url=app.docs_url, status_code=307
    )


@app.get(
    "/events/orders",
    tags=["Stream", "Tela Cozinha", "Tela Clientes", "Tela Entrega"]
)
async def list_orders_events(request: Request):
    """For the client-facing screen and the delivery tablet."""
    return StreamingResponse(
        event_stream(request, "orders"),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/products", tags=["ADM"])
async def create_products(
    name: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    priority: bool = Form(...),
    customizable: bool = Form(...),
    image_data: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    file_bytes = await image_data.read()
    return inserts.create_product_and_stock(
        session, name,  category,
        price, priority, customizable,
        file_bytes
    )


@app.get("/products", tags=["Tela Venda"])
async def list_products(session: Session = Depends(get_session)):
    return selects.list_products(session)


@app.get("/products/{id}/image", tags=["Tela Venda"])
async def list_products_images(
    id: int, session: Session = Depends(get_session)
):
    return selects.list_product_image(session, int(id))


@app.get("/products/categories", tags=["Tela Venda"])
async def list_categories(session: Session = Depends(get_session)):
    return selects.list_categories(session)


@app.post("/payments", tags=["Tela Venda"])
async def list_payments(pix_info: models.NewPix):
    return create_pix_qr_code(pix_info)


@app.post("/orders", tags=["Tela Venda"])
async def create_orders(
    order: models.NewOrder,
    session: Session = Depends(get_session)
):

    id = inserts.create_order_and_items(session, order)
    payload = json.dumps({"id": id, "status": enums.OrderStatus.queue.value})
    await sse_manager.publish("orders", payload)
    return {"id": id}


@app.get("/orders", tags=["Tela Cozinha", "Tela Clientes", "Tela Entrega"])
async def list_orders(
    id: int = Query(None),
    include: Optional[enums.IncludeOptions] = Query(None),
    sort: Optional[enums.SortOptions] = Query("updated_at"),
    status: Optional[list[enums.OrderStatus]] = Query(None),
    order: Optional[enums.SortOrderOptions] = Query(None),
    session: Session = Depends(get_session)
):
    filters = {
        "id": id,
        "include": include,
        "sort": sort,
        "list_status": status,
        "order": order
    }
    return selects.list_orders(session, filters)


@app.patch(
    "/orders/{id}/{status}",
    tags=["Tela Cozinha", "Tela Entrega", "ADM"]
)
async def alter_orders_status(
    id: int,
    status: enums.OrderStatus,
    session: Session = Depends(get_session)
):
    updates.alter_order_status(session, id, status)

    payload = json.dumps({"id": id, "status": status.value})
    await sse_manager.publish("orders", payload)
    return


@app.get("/stocks", tags=["Dashboard", "ADM"])
async def list_stocks(session: Session = Depends(get_session)):
    return selects.list_stock(session)


@app.post("/stocks", tags=["ADM"])
async def create_stocks(
    stocks: List[models.Stock],
    session: Session = Depends(get_session)
):
    return inserts.create_stock(session, stocks)


@app.post("/stocks/movements", tags=["ADM"])
async def create_stocks_movements(
    movement: models.StockMovement,
    session: Session = Depends(get_session)
):
    return inserts.create_stock_movement(session, movement)
