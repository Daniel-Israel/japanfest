from sqlalchemy.orm import Session

from app.api.operations import selects, updates
from app.util.enums import ReceiptType
from app.print.printer import print_client_receipt, print_kitchen_receipt


def _fetch_receipt_info(
    session: Session,
    order_id: int,
    type: ReceiptType
) -> dict:
    receipts = selects.list_receipts(session, order_id)
    for receipt in receipts:
        if receipt.get("type") == type:
            payment_method = receipt.get("payment_method")
            total_price = receipt.get("total_price")
            items = receipt.get("items")
    return payment_method, total_price, items


def print_receipt(session: Session, order_id: int, type: ReceiptType) -> str:
    payment_method, total_price, items = \
        _fetch_receipt_info(session, order_id, type)

    if type == ReceiptType.client.value:
        result = \
            print_client_receipt(order_id, payment_method, total_price, items)
    else:
        result = print_kitchen_receipt(order_id, items)

    updates.alter_receipt_status(session, order_id, type, result)
    return result
