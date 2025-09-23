from enum import Enum


class OrderStatus(Enum):
    created = "created"
    paid = "paid"
    delivered = "delivered"