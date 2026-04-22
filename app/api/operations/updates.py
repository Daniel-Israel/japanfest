from sqlalchemy import update
from sqlalchemy.orm import Session

from app.util.enums import OrderStatus
from app.db import orm


def alter_order_status(
        session: Session,
        id: int,
        new_status: OrderStatus
    ) -> None:
    sql = update(orm.Orders).where(orm.Orders.id == id).values(status=new_status.value)
    session.execute(sql)
    return
