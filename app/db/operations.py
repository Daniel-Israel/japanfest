import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Response

from app.db import orm


def to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def list_products(session: Session) -> pd.DataFrame:
    sql = select(
        orm.Products.id,
        orm.Products.name,
        orm.Products.category,
        orm.Products.price
    )
    result = session.execute(sql).scalars().all()
    return [to_dict(product) for product in result]
