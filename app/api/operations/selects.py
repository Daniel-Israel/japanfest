from sqlalchemy import select, func
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


def list_categories(session: Session) -> dict:
    categories = []
    sql = select(
        orm.Products.category
    ).distinct()
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
    )
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


def list_product_info(session: Session, id_: int) -> dict | None:
    sql = (
        select(
            orm.Products.id,
            orm.Products.name,
            orm.Products.category,
            orm.Products.price,
            orm.Products.priority,
        )
        .where(orm.Products.id == id_)
    )
    result = operations.select_one(session, sql)
    return dict(result) if result else None


def list_orders(session: Session) -> list[dict]:
    sql = (
        select(
            orm.Orders.id,
            orm.Orders.priority,
            orm.Orders.status,
        )
        .where(orm.Orders.status != OrderStatus.delivered.value)
    )
    rows = operations.select_many(session, sql)
    return [
        {"id": id_, "priority": priority, "status": status}
        for id_, priority, status in rows
    ]


def list_orders_items(session: Session) -> list[dict]:
    sql = (
        select(
            orm.Orders.id,
            orm.Orders.priority,
            orm.Orders.status,
            func.array_agg(orm.Products.name).label("products")
        )
        .join(orm.OrdersItems, orm.OrdersItems.order_id == orm.Orders.id)
        .join(orm.Products, orm.Products.id == orm.OrdersItems.product_id)
        .group_by(
            orm.Orders.id,
            orm.Orders.priority,
            orm.Orders.status,
        )
    )
    result = operations.select_many(session, sql)
    return [row._asdict() for row in result]
