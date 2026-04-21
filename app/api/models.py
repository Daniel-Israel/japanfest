from pydantic import BaseModel
from typing import List

from app.util.enums import PaymentMethod


class Item(BaseModel):
    id: int
    quantity: int
    unit_price: float


class NewOrder(BaseModel):
    list_items: List[Item]
    payment_method: PaymentMethod
    total_price: float
