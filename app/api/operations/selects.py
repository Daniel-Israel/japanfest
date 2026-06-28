from sqlalchemy import Select, select, func
from sqlalchemy.orm import Session
from fastapi import Response

from app.db import orm, operations
from app.util import enums


def check_priority(session: Session, list_products: list[int]) -> bool:
    sql = (
        select(orm.Products.priority)
        .where(orm.Products.id.in_(list_products))
        )
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

    if include in (
        enums.IncludeOptions.items,
        enums.IncludeOptions.items_and_customizations
    ):

        if include == enums.IncludeOptions.items_and_customizations:
            customizations_subquery = (
                select(
                    func.json_agg(orm.ProductCustomization.description)
                )
                .join(
                    orm.OrderItemCustomization,
                    orm.OrderItemCustomization.product_customization_id
                    == orm.ProductCustomization.id
                )
                .where(orm.OrderItemCustomization.order_item_id
                       == orm.OrdersItems.id)
                .correlate(orm.OrdersItems)
                .scalar_subquery()
            )
            item_json = func.json_build_object(
                "product_id",      orm.Products.id,
                "name",            orm.Products.name,
                "quantity",        orm.OrdersItems.quantity,
                "customizations",  customizations_subquery,
            )
        else:
            item_json = func.json_build_object(
                "product_id", orm.Products.id,
                "name",       orm.Products.name,
                "quantity",   orm.OrdersItems.quantity,
            )

        sql = (
            select(
                *columns,
                func.json_agg(item_json).label("products")
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
                sort_column.desc() if order_value
                == "desc" else sort_column.asc()
            )
    if id:
        sql = sql.where(orm.Orders.id == id)

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
        orm.Products.customizable,
        orm.Products.price
    ).order_by(orm.Products.name)
    result = operations.select_many(session, sql)
    return [
        {"name": name, "id": id, "category": category,
            "customizable": customizable, "price": price}
        for name, id, category, customizable, price in result
    ]


def list_product_customizations(session: Session, id: int) -> dict:
    sql = select(
        orm.ProductCustomization.id,
        orm.ProductCustomization.description
    ).where(orm.ProductCustomization.product_id == id)
    result = operations.select_many(session, sql)
    return [
        {"id": id, "description": description}
        for id, description in result
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

    query_result = []

    if filters.get("include") == enums.IncludeOptions.items:
        query_result = [
            {
                "id": id,
                "priority": priority,
                "status": status,
                "products": products
            }
            for id, priority, status, products in rows
        ]
    elif filters.get("include") == \
            enums.IncludeOptions.items_and_customizations:
        query_result = [
            {
                "id": id,
                "priority": priority,
                "status": status,
                "products": products
            }
            for id, priority, status, products in rows
        ]
    else:
        query_result = [
            {"id": id, "priority": priority, "status": status}
            for id, priority, status in rows
        ]
    return query_result


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


def list_receipts(session: Session, id: int = None) -> list[dict]:
    sql = (
        select(
            orm.Receipts.order_id,
            orm.Receipts.type,
            orm.Receipts.status,
            orm.Receipts.error_msg,
            orm.Orders.payment_method,
            orm.Orders.total_price,
            orm.Products.name,
            orm.OrdersItems.quantity,
            orm.OrdersItems.unit_price,
            orm.ProductCustomization.description,
        )
        .join(orm.Orders, orm.Receipts.order_id == orm.Orders.id)
        .join(
                orm.OrdersItems,
                orm.Receipts.order_id == orm.OrdersItems.order_id
            )
        .join(orm.Products, orm.OrdersItems.product_id == orm.Products.id)
        .outerjoin(
            orm.OrderItemCustomization,
            orm.OrdersItems.id == orm.OrderItemCustomization.order_item_id
        )
        .outerjoin(
            orm.ProductCustomization,
            orm.OrderItemCustomization.product_customization_id
            == orm.ProductCustomization.id
        )
        .order_by(orm.OrdersItems.id.desc())
    )
    if id is not None:
        sql = sql.where(orm.Receipts.order_id == id)

    result = operations.select_many(session, sql)

    receipts: dict[tuple, dict] = {}
    for (order_id, type, status, error_msg, payment_method,
         total_price, name, quantity, unit_price, description) in result:
        receipt_key = (order_id, type)
        if receipt_key not in receipts:
            receipts[receipt_key] = {
                "order_id": order_id,
                "type": type,
                "status": status,
                "error_msg": error_msg,
                "payment_method": payment_method,
                "total_price": total_price,
                "items": {},
            }

        item_key = (order_id, type, name)
        if item_key not in receipts[receipt_key]["items"]:
            receipts[receipt_key]["items"][item_key] = {
                "name": name,
                "quantity": quantity,
                "unit_price": unit_price,
                "customizations": [],
            }

        if description:
            (receipts[receipt_key]["items"][item_key]["customizations"]
             .append(description))

    for receipt in receipts.values():
        receipt["items"] = list(receipt["items"].values())

    return list(receipts.values())
