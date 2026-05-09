from pydantic import BaseModel
from typing import List, Optional

from app.util.enums import PaymentMethod, MovementType


class Item(BaseModel):
    id: int
    quantity: int
    unit_price: float


class NewOrder(BaseModel):
    list_items: List[Item]
    payment_method: PaymentMethod
    total_price: float


class NewPix(BaseModel):
    order_id: int
    total_price: float


class StockMovement(BaseModel):
    product_id: int
    order_id: Optional[int] = None
    quantity: int
    type: MovementType


class Stock(BaseModel):
    product_id: int
    quantity: int
