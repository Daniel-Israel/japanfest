import pika
import json

from os import getenv

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.models import NewOrder
from app.db.orm import Products, ProductCustomization
from app.db.operations import select_many


def _fetch_receipt_data(session: Session, order: NewOrder) -> dict:
    product_ids = [item.id for item in order.list_items]
    customization_ids = [
        c for item in order.list_items
        if item.customizations
        for c in item.customizations
    ]
    sql = select(
        Products.id,
        Products.name
    ).where(Products.id.in_(product_ids))
    products = select_many(session, sql)

    product_names = {row.id: row.name for row in products}

    if customization_ids:
        sql = select(
            ProductCustomization.id,
            ProductCustomization.description
        ).where(ProductCustomization.id.in_(customization_ids))
        customizations = select_many(session, sql)
        customization_descriptions = {
            row.id: row.description for row in customizations
        }

    return {
        "items": [
            {
                "product_name": product_names[item.id],
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "customizations": [
                    customization_descriptions[c]
                    for c in (item.customizations or [])
                ]
                if item.customizations
                else None
            }
            for item in order.list_items
        ]
    }


def publish_order_receipts(
    session: Session,
    channel,
    order_id: int,
    order: NewOrder
):

    receipt_data = _fetch_receipt_data(session, order)

    base = {
        "order_id": order_id,
        "payment_method": order.payment_method.value,
        "total_price": order.total_price,
        **receipt_data
    }

    for routing_key in ("receipt.client", "receipt.kitchen"):
        receipt_type = routing_key.split(".")[1]
        body = {**base, "receipt_type": receipt_type}

        if receipt_type == "kitchen":
            body.pop("payment_method")
            body.pop("total_price")
            body["items"] = [
                {
                    k: v for k, v in item.items()
                    if k != "unit_price"
                }
                for item in body["items"]
            ]

        channel.basic_publish(
            exchange=getenv("QUEUE_NAME", "receipts"),
            routing_key=routing_key,
            body=json.dumps(body),
            properties=pika.BasicProperties(delivery_mode=2)
        )
