from datetime import datetime

from sqlalchemy import Integer, String, Text, ForeignKey, BigInteger, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.base import Base

class Cart(Base):
    __tablename__ = "cart"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="RESTRICT")
    )

    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("product.id", ondelete="RESTRICT")
    )

    quantity: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    user: Mapped["User"] = relationship(
        "User", back_populates="cart", uselist=False
    )
    product: Mapped["Product"] = relationship(
        "Product", back_populates="cart", uselist=False
    )

    __table_args__ = (
        UniqueConstraint('user_id', 'product_id', name='_user_product_cart_uc'),
    )

