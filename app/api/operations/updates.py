from sqlalchemy import update
from sqlalchemy.orm import Session

from app.util.enums import OrderStatus, MovementType, IncludeOptions
from app.db import orm
from app.db.operations import _do_insert
from app.api.operations.selects import list_orders


def cancel_movement(session: Session, id: int) -> None:
    stock_movements = []

    order = list_orders(
        session, {"id": id, "include": IncludeOptions.items})[0]
    for product in order.get("products"):
        stock_movements.append(orm.StockMovements(
            product_id=product.get("product_id"),
            order_id=id,
            quantity=product.get("quantity"),
            type=MovementType.fix.value
        ))
    _do_insert(session, stock_movements)
    return


def alter_order_status(
    session: Session,
    id: int,
    new_status: OrderStatus
) -> None:
    if new_status == OrderStatus.canceled:
        cancel_movement(session, id)
    sql = (
        update(orm.Orders)
        .where(orm.Orders.id == id)
        .values(status=new_status.value)
    )
    session.execute(sql)
    return
