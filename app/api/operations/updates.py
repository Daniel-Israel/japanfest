from sqlalchemy import update
from sqlalchemy.orm import Session

from app.util.enums import OrderStatus, MovementType
from app.db import orm
from app.db.operations import _do_insert
from app.api.operations.selects import list_order_items


def alter_order_status(
        session: Session,
        id: int,
        new_status: OrderStatus
    ) -> None:
    sql = update(orm.Orders).where(orm.Orders.id == id).values(status=new_status.value)
    session.execute(sql)
    return


def cancel_order(session: Session, id: int) -> None:
    stock_movements = []

    order = list_order_items(session, id)

    for product in order:
        stock_movements.append(orm.StockMovements(
            product_id=product.get("id"),
            order_id=id,
            quantity=product.get("quantity"),
            type=MovementType.fix.value
        ))
    _do_insert(session, stock_movements)
    alter_order_status(session, id, OrderStatus.canceled)
    return
