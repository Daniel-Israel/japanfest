from sqlalchemy.orm import Session

from app.db import orm, operations
from app.api import models
from app.api.operations import selects
from app.util.enums import MovimentType
from app.util.conversions import to_dict



def create_product(
        session: Session, name: str, category: str,  
        price: float, priority: bool, image_data: bytes
    ):
    product = operations.insert_item(
        session,
        orm.Products(
            name=name, image_data=image_data, 
            category=category, price=price, 
            priority=priority
        )
    )
    product = to_dict(product)
    product.pop("image_data", None)
    
    return product


def create_stock_moviment(
        session: Session, moviment: models.StockMoviment) -> int:
    stock_moviment = orm.StockMoviments(
        product_id=moviment.product_id,
        order_id=moviment.order_id,
        quantity=moviment.quantity,
        type=moviment.type,
    )
    return operations.insert_item(session, stock_moviment)


def create_order(
    session: Session,
    order = models.NewOrder
) -> int:
    list_ids = []
    for item in order.list_items:
        list_ids.append(item.id)

    priority = selects.check_priority(session, list_ids)

    order = orm.Orders(
        payment_method=order.payment_method.value,
        priority=priority,
        total_price=order.total_price
    )

    return operations.insert_item(session, order).id
    

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
    operations.insert_list(session, order_items)
    operations.insert_list(session, moviments)
    return {"id": order_id}
