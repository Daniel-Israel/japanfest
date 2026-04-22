from sqlalchemy.orm import Session

from app.db import orm, operations
from app.api import models
from app.util.enums import MovimentType


def create_order(
    session: Session,
    order = models.NewOrder
) -> int:
    list_ids = []
    for item in order.list_items:
        list_ids.append(item.id)
    priority = operations.check_priority(session, list_ids)
    return operations.create_order(
        session, order.payment_method, priority, order.total_price)
    

def prepare_order_items(
        order_id: int, items: list[models.Item]) -> list[orm.OrdersItems]:
    order_items = []
    for item in items:
        order_items.append(orm.OrdersItems(
            order_id=order_id,
            product_id=item.id,
            quantity=item.quantity,
            unit_price=item.unit_price
        ))
    return order_items


def prepare_stock_moviments(
        list_items: list[orm.OrdersItems]) -> list[orm.StockMoviments]:
    list_moviments = []
    for item in list_items:
        list_moviments.append(orm.StockMoviments(
            product_id=item.product_id,
            order_id=item.order_id,
            quantity=-(item.quantity),
            type=MovimentType.sale.value
        ))
    return list_moviments


def create_order_and_items(session: Session, order = models.NewOrder) -> int:
    order_id = create_order(session, order)
    order_items = prepare_order_items(order_id, order.list_items)
    moviments = prepare_stock_moviments(order_items)
    operations.create_order_items(session, order_items)
    operations.create_stock_moviments(session, moviments)
    return {"id": order_id}