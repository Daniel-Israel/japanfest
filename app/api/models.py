from pydantic import BaseModel
from typing import Optional

from app.util.enums import PaymentMethod, MovementType, LossType


class Item(BaseModel):
    id: int
    quantity: int
    unit_price: float
    customizations: Optional[list[int]] = None


class NewOrder(BaseModel):
    list_items: list[Item]
    payment_method: PaymentMethod
    total_price: float


class NewCustomization(BaseModel):
    product_id: int
    description: str


class NewPix(BaseModel):
    order_id: int
    total_price: float


class NewStock(BaseModel):
    product_id: int
    quantity: int


class StockMovement(BaseModel):
    product_id: int
    order_id: Optional[int] = None
    quantity: int
    type: MovementType


class NewLosses(BaseModel):
    list_items: list[Item]
    loss_type: LossType
    total_price: float
