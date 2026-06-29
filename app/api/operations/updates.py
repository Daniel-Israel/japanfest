from sqlalchemy import update
from sqlalchemy.orm import Session

from app.util import enums
from app.db import orm
from app.db.operations import _do_insert, _execute
from app.api.operations.selects import list_orders


def cancel_movement(session: Session, id: int) -> None:
    stock_movements = []

    order = list_orders(
        session, {"id": id, "include": enums.IncludeOptions.items})[0]
    for product in order.get("products"):
        stock_movements.append(orm.StockMovements(
            product_id=product.get("product_id"),
            order_id=id,
            quantity=product.get("quantity"),
            type=enums.MovementType.fix.value
        ))
    _do_insert(session, stock_movements)
    return


def alter_order_status(
    session: Session,
    id: int,
    new_status: enums.OrderStatus
) -> None:
    if new_status == enums.OrderStatus.canceled:
        cancel_movement(session, id)
    sql = (
        update(orm.Orders)
        .where(orm.Orders.id == id)
        .values(status=new_status.value)
    )
    _execute(session, sql)
    return


def alter_receipt_status(
    session: Session,
    id: int,
    type: enums.ReceiptType,
    status: enums.ReceiptStatus,
) -> None:
    sql = (
        update(orm.Receipts)
        .where(orm.Receipts.order_id == id, orm.Receipts.type == type)
        .values(status=status)
    )
    _execute(session, sql)
