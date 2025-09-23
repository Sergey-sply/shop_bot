from datetime import datetime

from sqlalchemy import Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.base import Base


class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)

    products: Mapped[list["Product"]] = relationship(
        "Product", back_populates="category", uselist=True
    )
