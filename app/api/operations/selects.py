from sqlalchemy import Select, select, desc, func
from sqlalchemy.orm import Session
from fastapi import Response

from app.db import orm, operations
from app.util.enums import OrderStatus


def check_priority(session: Session, list_products: list[int]) -> bool:
    sql = select(orm.Products.priority).where(orm.Products.id.in_(list_products))
    priorities = session.execute(sql).scalars().all()
    if False in priorities:
        return False
    else:
        return True


def create_sql_orders_items(order_by) -> Select:
    sql = (
        select(
            orm.Orders.id,
            orm.Orders.priority,
            orm.Orders.status,
            func.json_agg(
                func.json_build_object(
                    "name", orm.Products.name,
                    "quantity",orm.OrdersItems.quantity,
                )
            ).label("products")
        )
        .join(orm.OrdersItems, orm.OrdersItems.order_id == orm.Orders.id)
        .join(orm.Products, orm.Products.id == orm.OrdersItems.product_id)
        .group_by(
            orm.Orders.id,
            orm.Orders.priority,
            orm.Orders.status,
        )
        .order_by(order_by)
    )
    return sql


def list_categories(session: Session) -> dict:
    categories = []
    sql = select(
        orm.Products.category
    ).distinct().order_by(orm.Products.category)
    result = operations.select_many(session, sql)
    for row in result:
        categories.append(row[0])
    return {"categories": categories}


def list_products(session: Session) -> dict:
    sql = select(
        orm.Products.name,
        orm.Products.id,
        orm.Products.category,
        orm.Products.price
    ).order_by(orm.Products.name)
    result = operations.select_many(session, sql)
    return [
        {"name": name, "id": id, "category": category, "price": price}
        for name, id, category, price in result
    ]


def list_product_image(session: Session, id: int) -> Response:
    sql = select(orm.Products.image_data).where(orm.Products.id == id)
    result = session.execute(sql).scalar_one()
    return Response(
        content=result, 
        media_type="image/jpeg",
    )


def list_orders(session: Session) -> list[dict]:
    sql = (
        select(
            orm.Orders.id,
            orm.Orders.priority,
            orm.Orders.status,
        )
        .where(
            orm.Orders.status != OrderStatus.delivered.value
            and
            orm.Orders.status != OrderStatus.canceled.value
            )
        .order_by(orm.Orders.id)
    )
    rows = operations.select_many(session, sql)
    return [
        {"id": id_, "priority": priority, "status": status}
        for id_, priority, status in rows
    ]


def list_order_items(session: Session, id: int) -> list[dict]:
    sql = (
        select(
            orm.Products.id,
            orm.OrdersItems.quantity,
        )
        .join(orm.OrdersItems, orm.OrdersItems.product_id == orm.Products.id)
        .where(orm.OrdersItems.order_id == id)
    )
    result = session.execute(sql).all()
    return [row._asdict() for row in result]


def list_orders_items(session: Session) -> list[dict]:
    result = operations.select_many(
        session, 
        create_sql_orders_items(orm.Orders.id)
    )
    return [row._asdict() for row in result]


def list_new_order_items(session: Session) -> list[dict]:
    result = operations.select_many(
        session, 
        create_sql_orders_items(desc(orm.Orders.updated_at))
    )
    return [row._asdict() for row in result]


def list_stock(session: Session) -> list[dict]:
    sql = (
        select(orm.Stocks.product_id, orm.Stocks.quantity)
        .order_by(orm.Stocks.product_id)
    )
    result = operations.select_many(session, sql)
    return [
        {"product_id": product_id, "quantity": quantity}
        for product_id, quantity in result
    ]
