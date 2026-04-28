from sqlalchemy import Select, select, func
from sqlalchemy.orm import Session
from fastapi import Response

from app.db import orm, operations
from app.util import enums

def check_priority(session: Session, list_products: list[int]) -> bool:
    sql = select(orm.Products.priority).where(orm.Products.id.in_(list_products))
    priorities = session.execute(sql).scalars().all()
    if False in priorities:
        return False
    else:
        return True


def create_sql_list_orders(
    id: int = None,
    include: enums.IncludeOptions = None,
    sort: enums.SortOptions = None,
    list_status: list[enums.OrderStatus] = None,
    order: enums.SortOrderOptions = None
) -> Select:

    columns = [
        orm.Orders.id,
        orm.Orders.priority,
        orm.Orders.status,
    ]
    if include == enums.IncludeOptions.items:
        sql = (
            select(
                *columns,
                func.json_agg(
                    func.json_build_object(
                        "product_id", orm.Products.id,
                        "name", orm.Products.name,
                        "quantity", orm.OrdersItems.quantity,
                    )
                ).label("products")
            )
            .join(orm.OrdersItems, orm.OrdersItems.order_id == orm.Orders.id)
            .join(orm.Products, orm.Products.id == orm.OrdersItems.product_id)
            .group_by(*columns)
        )
    else:
        sql = select(*columns)

    if list_status:
        status_values = [s.value for s in list_status]
        sql = sql.where(orm.Orders.status.in_(status_values))

    if sort:
        sort_column = getattr(orm.Orders, sort.value, None)
        if sort_column is not None:
            order_value = order.value if order else "asc"
            sql = sql.order_by(
                sort_column.desc() if order_value == "desc" else sort_column.asc()
            )

    if id:
        sql = sql.where(orm.Orders.id==id)

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


def list_orders(session: Session, filters: dict) -> list[dict]:
    filters = {k: v for k, v in filters.items() if v is not None}
    sql = create_sql_list_orders(**filters)
    rows = operations.select_many(session, sql)

    if filters.get("include") == enums.IncludeOptions.items:
        return [
            {"id": id, "priority": priority, "status": status, "products": products}
            for id, priority, status, products in rows
        ]
    return [
        {"id": id, "priority": priority, "status": status}
        for id, priority, status in rows
    ]


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
