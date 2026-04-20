from datetime import datetime
 
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    LargeBinary,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
 
from app.util import enums

 
class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"
 
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    image_data: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    category: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    priority: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
 
 
class Order(Base):
    __tablename__ = "orders"
 
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    status: Mapped[enums.OrderStatus] = mapped_column(
        Enum(enums.OrderStatus, name="order_status"), nullable=False, default=enums.OrderStatus.queue
    )
    priority: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    payment_method: Mapped[enums.PaymentMethod] = mapped_column(
        Enum(enums.PaymentMethod, name="payment_method"), nullable=False
    )
    total_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
 
 
class OrderItem(Base):
    __tablename__ = "orders_items"
 
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orders.id"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("products.id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
 
 
class Stock(Base):
    __tablename__ = "stock"
 
    product_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("products.id"), primary_key=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
 
 
class StockMoviment(Base):
    __tablename__ = "stock_moviments"
 
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("products.id"), nullable=False
    )
    order_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("orders.id"), nullable=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[enums.MovimentType] = mapped_column(
        Enum(enums.MovimentType, name="moviment_type"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
