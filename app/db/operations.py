import pandas as pd
from sqlalchemy import select, insert
from sqlalchemy.orm import Session
from fastapi import Response

from app.db import orm
from app.util.enums import PaymentMethod, OrderStatus


def to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def check_priority(session: Session, list_products: list[int]) -> bool:
    sql = select(orm.Products.priority).where(orm.Products.id.in_(list_products))
    priorities = session.execute(sql).scalars().all()
    if False in priorities:
        return False
    else:
        return True


def list_products(session: Session) -> pd.DataFrame:
    sql = select(
        orm.Products.name,
        orm.Products.id,
        orm.Products.category,
        orm.Products.price
    )
    result = session.execute(sql).all()
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
    result = session.execute(sql).mappings().first()
    return dict(result) if result else None


def list_orders(session: Session) -> dict:
    sql = select(
        orm.Orders.id,
        orm.Orders.priority,
        orm.Orders.status
    ).where(orm.Orders.status != OrderStatus.delivered.value)
    result = session.execute(sql).all()
    return [
        {"id": id, "priority": priority ,"status": status}
        for id, priority, status in result
    ]


def create_product(session: Session, product: orm.Products):
    session.add(product)
    session.commit()
    session.refresh(product)
    return {"id": product.id, "name": product.name}


def create_order(
        session: Session, 
        payment_method: PaymentMethod,
        priority: bool,
        total_price: float
    ) -> int:
    order = orm.Orders(
        payment_method=payment_method.value,
        priority=priority,
        total_price=total_price
    )
    session.add(order)
    session.commit()
    session.refresh(order)
    return order.id
