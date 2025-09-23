
from sqlalchemy import Integer, String, Text, ForeignKey, BigInteger, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.base import Base


class DeliveryMethod(Base):
    __tablename__ = "delivery_method"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        unique=True
    )

    orders: Mapped[list["Order"]] = relationship(
        "Order", back_populates="delivery_method", uselist=True
    )
