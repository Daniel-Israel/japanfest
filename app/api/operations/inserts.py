from sqlalchemy.orm import Session

from app.db import orm, operations
from app.api import models
from app.api.operations import selects
from app.util.enums import MovementType, ReceiptType
from app.util.conversions import to_dict
from app.api.operations.print import print_receipt


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


def _insert_order(
    session: Session,
    order: models.NewOrder,
    priority: bool
) -> int:
    new_order = orm.Orders(
        payment_method=order.payment_method.value,
        priority=priority,
        total_price=order.total_price,
    )
    return operations._do_insert(session, [new_order])[0].id


def _insert_order_items(
    session: Session, order_id: int, items: list[models.Item]
) -> list[orm.OrdersItems]:
    order_items = [
        orm.OrdersItems(
            order_id=order_id,
            product_id=item.id,
            quantity=item.quantity,
            unit_price=item.unit_price,
        )
        for item in items
    ]
    return operations._do_insert(session, order_items)


def _insert_customizations(
    session: Session,
    order_items: list[orm.OrdersItems],
    items: list[models.Item],
) -> None:
    customizations = [
        orm.OrderItemCustomization(
            order_item_id=order_item.id,
            product_customization_id=customization_id,
        )
        for order_item, item in zip(order_items, items)
        if item.customizations
        for customization_id in item.customizations
    ]
    if customizations:
        operations._do_insert(session, customizations)


def _insert_stock_movements(
    session: Session,
    order_items: list[orm.OrdersItems]
) -> None:
    movements = [
        orm.StockMovements(
            product_id=item.product_id,
            order_id=item.order_id,
            quantity=-(item.quantity),
            type=MovementType.sale.value,
        )
        for item in order_items
    ]
    operations._do_insert(session, movements)


def _insert_order_receipts(session: Session, order_id: int):
    receipts = []
    for type in [ReceiptType.client.value, ReceiptType.kitchen.value]:
        receipts.append(
            orm.Receipts(
                order_id=order_id,
                type=type,
            )
        )
        operations._do_insert(session, receipts)


def create_order_and_items(session: Session, order: models.NewOrder) -> int:
    item_ids = [item.id for item in order.list_items]
    priority = selects.check_priority(session, item_ids)
    order_id = _insert_order(session, order, priority)
    order_items = _insert_order_items(session, order_id, order.list_items)
    _insert_stock_movements(session, order_items)
    _insert_customizations(session, order_items, order.list_items)
    _insert_order_receipts(session, order_id)
    print_receipt(session, order_id, ReceiptType.client)
    return order_id


def create_stock(
    session: Session, stocks: list[models.NewStock]
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
    stock = [models.NewStock(product_id=product.get("id"), quantity=0)]
    create_stock(session, stock)
    return product
