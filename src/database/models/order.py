from datetime import datetime
from uuid import UUID

from sqlalchemy import Integer, String, ForeignKey, BigInteger, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM

from uuid6 import uuid7

from src.core.enums.order import OrderStatus
from src.database.models.base import Base

class Order(Base):
    __tablename__ = "order"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid7
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="RESTRICT")
    )

    delivery_method_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("delivery_method.id", ondelete="RESTRICT")
    )

    status: Mapped[OrderStatus] = mapped_column(
        PG_ENUM(OrderStatus, name="order_status"),
        nullable=False
    )

    client_name: Mapped[str] = mapped_column(String, nullable=False)
    client_number: Mapped[str] = mapped_column(String(12), nullable=False)
    client_address: Mapped[str] = mapped_column(String, nullable=False)

    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    user: Mapped["User"] = relationship(
        "User", back_populates="orders", uselist=False
    )
    delivery_method: Mapped["DeliveryMethod"] = relationship(
        "DeliveryMethod", back_populates="orders", uselist=False
    )
    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", uselist=True
    )


class OrderItem(Base):
    __tablename__ = "order_item"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    order_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("order.id", ondelete="CASCADE"),
    )

    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("product.id", ondelete="RESTRICT")
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    unit_price: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )

    order: Mapped["Order"] = relationship(
        "Order", back_populates="order_items", uselist=False
    )
    product: Mapped["Product"] = relationship(
        "Product", back_populates="order_items", uselist=False
    )

