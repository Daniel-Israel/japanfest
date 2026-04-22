from sqlalchemy import select, update, func, Select, Sequence, RowMapping
from sqlalchemy.orm import Session
from fastapi import Response

from app.db import orm
from app.util.enums import OrderStatus
from app.util.types import ORMOBJECT


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
    result = select_many(session, sql)
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
    result = select_many(session, sql)
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


def list_product_info(session: Session, id: int) -> dict:
    sql = select(
        orm.Products.id,
        orm.Products.name,
        orm.Products.category,
        orm.Products.price,
        orm.Products.priority,
    ).where(orm.Products.id == id)
    result = select_one(session, sql)
    return dict(result) if result else None


def list_orders(session: Session) -> dict:
    sql = select(
        orm.Orders.id,
        orm.Orders.priority,
        orm.Orders.status
    ).where(orm.Orders.status != OrderStatus.delivered.value)
    result = select_many(session, sql)
    return [
        {"id": id, "priority": priority ,"status": status}
        for id, priority, status in result
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
    result = select_many(session, sql)
    return [row._asdict() for row in result]


def insert_list(session: Session, list_items: list[ORMOBJECT]) -> list[ORMOBJECT]:
    session.add_all(list_items)
    session.commit()
    for item in list_items:
        session.refresh(item)
    return


def insert_item(session: Session, item: ORMOBJECT) -> ORMOBJECT:
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def select_one(session: Session, sql: Select) -> RowMapping | None:
    return session.execute(sql).mappings().first()


def select_many(session: Session, sql: Select) -> Sequence:
    return session.execute(sql).all()


def alter_order_status(
        session: Session,
        id: int,
        new_status: OrderStatus
    ) -> None:
    sql = update(orm.Orders).where(orm.Orders.id == id).values(status=new_status.value)
    session.execute(sql)
    return
