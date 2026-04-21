from sqlalchemy.orm import Session

from app.db import orm, operations
from app.api import models
from app.util import enums


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
    

def prepare_order_items(session: Session, order_id: int, items: list[models.Item]):
    pass
