from datetime import datetime

from sqlalchemy import Integer, String, Text, ForeignKey, BigInteger, DateTime, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.base import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(32),
        nullable=False
    )

    created: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

    cart: Mapped[list["Cart"]] = relationship(
        "Cart", back_populates="user", uselist=True
    )
    orders: Mapped[list["Order"]] = relationship(
        "Order", back_populates="user", uselist=True
    )
    roles: Mapped[list["Role"]] = relationship(
        secondary="user_role", back_populates="users", uselist=True
    )


class Role(Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        unique=True
    )

    users: Mapped[list["User"]] = relationship(
        secondary="user_role", back_populates="roles", uselist=True
    )


class UserRole(Base):
    __tablename__ = "user_role"

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True
    )
    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("role.id", ondelete="CASCADE"),
        primary_key=True
    )
