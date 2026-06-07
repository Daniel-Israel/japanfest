from typing import List

from sqlalchemy.orm import Session

from app.db import orm, operations
from app.api import models
from app.api.operations import selects
from app.util.enums import MovementType
from app.util.conversions import to_dict


def create_product(
    session: Session, name: str, category: str,
    price: float, priority: bool, customizable: bool,
    image_data: bytes
) -> dict:
    product = operations._do_insert(
        session,
        [orm.Products(
            name=name, image_data=image_data,
            category=category, price=price,
            priority=priority, customizable=customizable
        )]
    )
    product = to_dict(product[0])
    product.pop("image_data", None)

    return product


def create_customization(
    session: Session, customization: models.NewCustomization
) -> dict:
    customization = operations._do_insert(
        session,
        [orm.ProductCustomization(
            product_id=customization.product_id,
            description=customization.description
        )]
    )

    return customization


def create_stock_movement(
    session: Session, movement: models.StockMovement
) -> int:
    stock_movement = orm.StockMovements(
        product_id=movement.product_id,
        order_id=movement.order_id,
        quantity=movement.quantity,
        type=movement.type,
    )
    return operations._do_insert(session, [stock_movement])


def create_order(
    session: Session,
    order: models.NewOrder
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

    return operations._do_insert(session, [order])[0].id


def prepare_order_items(
    order_id: int, items: list[models.Item]
) -> list[orm.OrdersItems]:
    order_items = []
    for item in items:
        order_items.append(orm.OrdersItems(
            order_id=order_id,
            product_id=item.id,
            quantity=item.quantity,
            unit_price=item.unit_price
        ))
    return order_items


def prepare_stock_movements(
    list_items: list[orm.OrdersItems]
) -> list[orm.StockMovements]:
    list_movements = []
    for item in list_items:
        list_movements.append(orm.StockMovements(
            product_id=item.product_id,
            order_id=item.order_id,
            quantity=-(item.quantity),
            type=MovementType.sale.value
        ))
    return list_movements


def create_order_and_items(
    session: Session, order: models.NewOrder
) -> int:
    order_id = create_order(session, order)
    order_items = prepare_order_items(order_id, order.list_items)
    movements = prepare_stock_movements(order_items)
    operations._do_insert(session, order_items)
    operations._do_insert(session, movements)
    return order_id


def create_stock(
    session: Session, stocks: List[models.Stock]
) -> orm.Stocks:
    list_stocks = []
    for stock in stocks:
        list_stocks.append(orm.Stocks(
            product_id=stock.product_id,
            quantity=stock.quantity
        ))
    list_stocks = operations._do_insert(session, list_stocks)


def create_product_and_stock(
    session: Session, name: str, category: str,
    price: float, priority: bool, customizable: bool,
    image_data: bytes
) -> dict:
    product = create_product(
        session, name, category, price, priority, customizable, image_data)
    stock = [models.Stock(product_id=product.get("id"), quantity=0)]
    create_stock(session, stock)
    return product
