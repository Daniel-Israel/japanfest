import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Response

from app.db import orm


def to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def list_products(session: Session) -> pd.DataFrame:
    sql = select(
        orm.Products.name,
        orm.Products.category,
        orm.Products.price
    )
    result = session.execute(sql).all()
    return [
        {"name": name, "category": category, "price": price}
        for name, category, price in result
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


def create_product(session: Session, product: orm.Products):
    session.add(product)
    session.commit()
    session.refresh(product)
    return {"id": product.id, "name": product.name}
