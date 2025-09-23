from datetime import datetime

from sqlalchemy import Integer, String, Text, ForeignKey, BigInteger, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.base import Base


class Product(Base):
    __tablename__ = "product"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("category.id", ondelete="RESTRICT")
    )

    name: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[str] = mapped_column(String(128), nullable=False)
    image: Mapped[str] = mapped_column(String, nullable=True)
    price: Mapped[int] = mapped_column(BigInteger, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    category: Mapped["Category"] = relationship(
        "Category", back_populates="products", uselist=False
    )

    cart: Mapped[list["Cart"]] = relationship(
        "Cart", back_populates="product", uselist=True
    )

    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="product", uselist=True
    )